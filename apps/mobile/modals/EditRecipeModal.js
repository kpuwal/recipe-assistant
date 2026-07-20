// EditRecipeModal.js - Modal for editing an existing recipe
import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Modal,
  Keyboard,
  TouchableWithoutFeedback,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { KeyboardAwareScrollView } from "react-native-keyboard-aware-scroll-view";
import axios from "axios";
import { Ionicons } from "@expo/vector-icons";

const EditRecipeModal = ({
  visible, 
  recipe, 
  api_url, 
  onClose, 
  onRecipeUpdated 
 }) => {
  const [form, setForm] = useState({
    title: "",
    persons: "",
    time_minutes: "",
    category: "",
    ingredients: [{ name: "", quantity: "" }],
    steps: [""],
    tips: "",
    image: "",
  });

  // Populate form when a recipe is provided
  useEffect(() => {
    if (recipe) {
      setForm({
        title: recipe.title || "",
        persons: recipe.persons ? String(recipe.persons) : "",
        time_minutes: recipe.time_minutes ? String(recipe.time_minutes) : "",
        category: recipe.category || "",
        ingredients: recipe.ingredients?.length ? recipe.ingredients : [{ name: "", quantity: "" }],
        steps: recipe.steps?.length ? recipe.steps : [""],
        tips: recipe.tips || "",
        image: recipe.image || "",
      });
    }
  }, [recipe]);

  const updateField = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }));
  };

  const updateIngredient = (index, field, value) => {
    const newIngredients = [...form.ingredients];
    newIngredients[index][field] = value;
    setForm(prev => ({ ...prev, ingredients: newIngredients }));
  };

  const addIngredient = () => {
    setForm(prev => ({
      ...prev,
      ingredients: [...prev.ingredients, { name: "", quantity: "" }],
    }));
  };

  const removeIngredient = index => {
    if (form.ingredients.length === 1) return;
    setForm(prev => ({
      ...prev,
      ingredients: prev.ingredients.filter((_, i) => i !== index),
    }));
  };

  const addStep = () => {
    setForm(prev => ({ ...prev, steps: [...prev.steps, ""] }));
  };

  const removeStep = index => {
    if (form.steps.length === 1) return;
    setForm(prev => ({
      ...prev,
      steps: prev.steps.filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = async () => {
    if (!form.title.trim()) {
      Alert.alert("Error", "Recipe title is required");
      return;
    }
    const validIngredients = form.ingredients.filter(ing => ing.name.trim());
    const recipeData = {
      title: form.title.trim(),
      source: "personal",
      persons: form.persons ? parseInt(form.persons) : null,
      time_minutes: form.time_minutes ? parseInt(form.time_minutes) : null,
      category: form.category.trim() || "other",
      ingredients: validIngredients,
      steps: form.steps.filter(s => s.trim()),
      tips: form.tips.trim() || null,
      image: form.image.trim() || null,
    };
    try {
      const response = await axios.put(`${api_url}/recipes/${recipe.id}`, recipeData);
      onRecipeUpdated?.(response.data);
      onClose();
    } catch (error) {
      console.error(error);
      Alert.alert("Error", "Failed to update recipe. Please try again.");
    }
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="fullScreen"
      onRequestClose={onClose}
    >
      <SafeAreaView style={styles.modalContainer}>
        <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
          <KeyboardAwareScrollView
            enableOnAndroid
            extraScrollHeight={80}
            keyboardOpeningTime={0}
            keyboardShouldPersistTaps="handled"
            keyboardDismissMode="on-drag"
            showsVerticalScrollIndicator={false}
            contentContainerStyle={styles.scrollContent}
          >
            <View style={styles.header}>
              <TouchableOpacity onPress={onClose} style={styles.closeButton}>
                <Ionicons name="close" size={28} color="#333" />
              </TouchableOpacity>
              <Text style={styles.title}>✏️ Edit Recipe</Text>
            </View>

            {/* Form – same structure as AddRecipeModal */}
            <TextInput
              style={styles.input}
              placeholder="Recipe Title *"
              value={form.title}
              onChangeText={v => updateField("title", v)}
            />
            <View style={styles.row}>
              <TextInput
                style={[styles.input, { flex: 1 }]}
                placeholder="Persons"
                keyboardType="number-pad"
                value={form.persons}
                onChangeText={v => updateField("persons", v)}
              />
              <TextInput
                style={[styles.input, { flex: 1 }]}
                placeholder="Time (min)"
                keyboardType="number-pad"
                value={form.time_minutes}
                onChangeText={v => updateField("time_minutes", v)}
              />
            </View>
            <TextInput
              style={styles.input}
              placeholder="Category"
              value={form.category}
              onChangeText={v => updateField("category", v)}
            />

            <Text style={styles.sectionTitle}>Ingredients</Text>
            {form.ingredients.map((ing, idx) => (
              <View key={idx} style={styles.ingredientRow}>
                <TextInput
                  style={[styles.input, { flex: 2 }]}
                  placeholder="Quantity"
                  value={ing.quantity}
                  onChangeText={v => updateIngredient(idx, "quantity", v)}
                />
                <TextInput
                  style={[styles.input, { flex: 3 }]}
                  placeholder="Ingredient name *"
                  value={ing.name}
                  onChangeText={v => updateIngredient(idx, "name", v)}
                />
                <TouchableOpacity onPress={() => removeIngredient(idx)} style={styles.removeBtn}>
                  <Text style={styles.removeText}>✕</Text>
                </TouchableOpacity>
              </View>
            ))}
            <TouchableOpacity style={styles.addBtn} onPress={addIngredient}>
              <Text style={styles.addBtnText}>+ Add Ingredient</Text>
            </TouchableOpacity>

            <Text style={styles.sectionTitle}>Preparation Steps</Text>
            {form.steps.map((step, idx) => (
              <View key={idx} style={styles.listItem}>
                <TextInput
                  style={[styles.input, styles.stepInput]}
                  placeholder={`Step ${idx + 1}`}
                  multiline
                  textAlignVertical="top"
                  value={step}
                  onChangeText={v => {
                    const newSteps = [...form.steps];
                    newSteps[idx] = v;
                    updateField("steps", newSteps);
                  }}
                />
                <TouchableOpacity onPress={() => removeStep(idx)} style={styles.removeBtn}>
                  <Text style={styles.removeText}>✕</Text>
                </TouchableOpacity>
              </View>
            ))}
            <TouchableOpacity style={styles.addBtn} onPress={addStep}>
              <Text style={styles.addBtnText}>+ Add Step</Text>
            </TouchableOpacity>

            <TextInput
              style={[styles.input, styles.tipsInput]}
              placeholder="Tips (optional)"
              multiline
              textAlignVertical="top"
              value={form.tips}
              onChangeText={v => updateField("tips", v)}
            />
            <TextInput
              style={styles.input}
              placeholder="Image URL (optional)"
              autoCapitalize="none"
              keyboardType="url"
              value={form.image}
              onChangeText={v => updateField("image", v)}
            />
            <View style={styles.buttonRow}>
              <TouchableOpacity style={styles.cancelBtn} onPress={onClose}>
                <Text style={styles.cancelText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.saveBtn} onPress={handleSubmit}>
                <Text style={styles.saveText}>Save Changes</Text>
              </TouchableOpacity>
            </View>
          </KeyboardAwareScrollView>
        </TouchableWithoutFeedback>
      </SafeAreaView>
    </Modal>
  );
};

const styles = StyleSheet.create({
  modalContainer: { flex: 1, backgroundColor: "#fff" },
  scrollContent: { padding: 20, paddingBottom: 80, flexGrow: 1 },
  header: { flexDirection: "row", alignItems: "center", paddingTop: 20, paddingBottom: 15, borderBottomWidth: 1, borderBottomColor: "#eee" },
  closeButton: { marginRight: 35 },
  title: { fontSize: 28, fontWeight: "bold", color: "#1a1a1a", flex: 1 },
  row: { flexDirection: "row", gap: 12 },
  input: { borderWidth: 1, borderColor: "#ddd", borderRadius: 12, paddingHorizontal: 14, paddingVertical: 14, fontSize: 16, backgroundColor: "#fafafa", marginBottom: 12 },
  ingredientRow: { flexDirection: "row", alignItems: "center", gap: 8, marginBottom: 12 },
  listItem: { flexDirection: "row", alignItems: "flex-start", marginBottom: 8 },
  removeBtn: { marginLeft: 8, marginTop: 10, padding: 6 },
  removeText: { color: "#e74c3c", fontSize: 22, fontWeight: "bold" },
  addBtn: { backgroundColor: "#f5f5f5", paddingVertical: 14, borderRadius: 12, alignItems: "center", marginBottom: 16 },
  addBtnText: { color: "#e74c3c", fontWeight: "600", fontSize: 16 },
  sectionTitle: { fontSize: 18, fontWeight: "600", marginTop: 20, marginBottom: 10, color: "#333" },
  stepInput: { flex: 1, minHeight: 90 },
  tipsInput: { minHeight: 100 },
  buttonRow: { flexDirection: "row", justifyContent: "space-between", marginTop: 30, marginBottom: 30 },
  cancelBtn: { paddingHorizontal: 24, paddingVertical: 16, justifyContent: "center" },
  cancelText: { color: "#666", fontSize: 16, fontWeight: "600" },
  saveBtn: { backgroundColor: "#e74c3c", paddingHorizontal: 32, paddingVertical: 16, borderRadius: 12 },
  saveText: { color: "#fff", fontWeight: "700", fontSize: 16 },
});

export default EditRecipeModal;
