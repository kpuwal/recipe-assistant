import React, { useState } from "react";
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

const AddRecipeModal = ({ visible, onClose, api_url, onRecipeAdded }) => {
  const [form, setForm] = useState({
    title: "",
    persons: "",
    time_minutes: "",
    category: "other",
    ingredients: [{ name: "", quantity: "" }],
    steps: [""],
    tips: "",
    image: "",
  });

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
      ingredients: [...prev.ingredients, { name: "", quantity: "" }]
    }));
  };

  const removeIngredient = (index) => {
    if (form.ingredients.length === 1) return;
    setForm(prev => ({
      ...prev,
      ingredients: prev.ingredients.filter((_, i) => i !== index),
    }));
  };

  const addStep = () => {
    setForm(prev => ({ ...prev, steps: [...prev.steps, ""] }));
  };

  const removeStep = (index) => {
    if (form.steps.length === 1) return;
    setForm(prev => ({
      ...prev,
      steps: prev.steps.filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = async () => {
    if (!form.title.trim()) {
      Alert.alert("Fout", "Recept titel is verplicht");
      return;
    }

    const validIngredients = form.ingredients.filter(ing => ing.name.trim());
    if (validIngredients.length === 0) {
      Alert.alert(
        "Fout", 
        "Voeg ten minste één ingrediënt met een naam toe"
      );
      return;
    }

    const validSteps = form.steps.filter(s => s.trim());
    if (validSteps.length === 0) {
      Alert.alert(
        "Fout", 
        "Voeg ten minste één bereidingsstap toe"
      );
      return;
    }

    const recipe_data = {
      title: form.title.trim(),
      source: "personal",
      persons: form.persons ? parseInt(form.persons) : null,
      time_minutes: form.time_minutes ? parseInt(form.time_minutes) : null,
      category: form.category.trim() || "other",
      ingredients: validIngredients,
      steps: validSteps,
      tips: form.tips.trim() || null,
      image: form.image.trim() || null,
    };

    try {
      const response = await axios.post(`${api_url}/recipes/`, recipe_data);
      
      onRecipeAdded?.(response.data);
      onClose();

      setForm({
        title: "",
        persons: "",
        time_minutes: "",
        category: "other",
        ingredients: [{ name: "", quantity: "" }],
        steps: [""],
        tips: "",
        image: "",
      });
    } catch (error) {
      console.error(error);
      Alert.alert("Fout", "Kon recept niet opslaan. Probeer het opnieuw.");
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
            {/* <Text style={styles.title}>🍳 Add New Recipe</Text> */}
            <View style={styles.header}>
                <TouchableOpacity onPress={onClose} style={styles.closeButton}>
                    <Ionicons name="close" size={28} color="#333" />
                </TouchableOpacity>
                <Text style={styles.title}>🍳 Add New Recipe</Text>
            </View>

            <TextInput
                style={styles.input}
                placeholder="Recipe Title *"
                returnKeyType="next"
                value={form.title}
                onChangeText={(v) => updateField("title", v)}
            />

            <View style={styles.row}>
                <TextInput
                style={[styles.input, { flex: 1 }]}
                placeholder="Persons"
                keyboardType="number-pad"
                returnKeyType="next"
                value={form.persons}
                onChangeText={(v) => updateField("persons", v)}
                />

                <TextInput
                style={[styles.input, { flex: 1 }]}
                placeholder="Time (min)"
                keyboardType="number-pad"
                returnKeyType="next"
                value={form.time_minutes}
                onChangeText={(v) => updateField("time_minutes", v)}
                />
            </View>

            <TextInput
                style={styles.input}
                placeholder="Category (e.g. pasta, curry...)"
                returnKeyType="next"
                value={form.category}
                onChangeText={(v) => updateField("category", v)}
            />

            <Text style={styles.sectionTitle}>Ingredients</Text>

            {form.ingredients.map((ing, index) => (
              <View key={index} style={styles.ingredientRow}>
                <TextInput
                  style={[styles.input, { flex: 2 }]}
                  placeholder="Quantity (e.g. 200g, 1) *"
                  value={ing.quantity}
                  onChangeText={(v) => updateIngredient(index, "quantity", v)}
                />
                <TextInput
                  style={[styles.input, { flex: 3 }]}
                  // placeholder="Ingredient name *"
                  placeholder={
                      index === 0 
                        ? "Ingredient name *"
                        : `Ingredient name`
                    }
                  value={ing.name}
                  onChangeText={(v) => updateIngredient(index, "name", v)}
                />

                <TouchableOpacity
                  onPress={() => removeIngredient(index)}
                  style={styles.removeBtn}
                >
                  <Text style={styles.removeText}>✕</Text>
                </TouchableOpacity>
              </View>
            ))}

            <TouchableOpacity style={styles.addBtn} onPress={addIngredient}>
                <Text style={styles.addBtnText}>+ Add Ingredient</Text>
            </TouchableOpacity>

            <Text style={styles.sectionTitle}>Preparation Steps</Text>

            {form.steps.map((step, index) => (
                <View key={index} style={styles.listItem}>
                <TextInput
                    style={[styles.input, styles.stepInput]}
                    placeholder={
                      index === 0 
                        ? "Step 1 *" 
                        : `Step ${index + 1}`
                    }
                    multiline
                    textAlignVertical="top"
                    returnKeyType="default"
                    value={step}
                    onChangeText={(v) => {
                    const newSteps = [...form.steps];
                    newSteps[index] = v;
                    updateField("steps", newSteps);
                    }}
                />

                <TouchableOpacity
                    onPress={() => removeStep(index)}
                    style={styles.removeBtn}
                >
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
                onChangeText={(v) => updateField("tips", v)}
            />

            <TextInput
                style={styles.input}
                placeholder="Image URL (optional)"
                autoCapitalize="none"
                keyboardType="url"
                returnKeyType="done"
                value={form.image}
                onChangeText={(v) => updateField("image", v)}
            />

            <View style={styles.buttonRow}>
                <TouchableOpacity
                style={styles.cancelBtn}
                onPress={onClose}
                >
                <Text style={styles.cancelText}>Cancel</Text>
                </TouchableOpacity>

                <TouchableOpacity
                style={styles.saveBtn}
                onPress={handleSubmit}
                >
                <Text style={styles.saveText}>Save Recipe</Text>
                </TouchableOpacity>
            </View>
            </KeyboardAwareScrollView>
        </TouchableWithoutFeedback>
        </SafeAreaView>
    </Modal>
    );
};

const styles = StyleSheet.create({
  modalContainer: {
    flex: 1,
    backgroundColor: "#fff",
  },

  scrollContent: {
    padding: 20,
    paddingBottom: 80,
    flexGrow: 1,
  },

  header: {
    backgroundColor: "#fff",
    paddingTop: 20,
    paddingBottom: 15,
    paddingHorizontal: 5,
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
    flexDirection: "row",
    alignItems: "center",
  },

  closeButton: {
    marginRight: 35,
  },

  title: {
    fontSize: 28,
    fontWeight: "bold",
    color: "#1a1a1a",
    flex: 1,
  },

  row: {
    flexDirection: "row",
    gap: 12,
  },

  input: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 14,
    fontSize: 16,
    backgroundColor: "#fafafa",
    marginBottom: 12,
  },

  stepInput: {
    flex: 1,
    minHeight: 90,
  },

  tipsInput: {
    minHeight: 100,
  },

  sectionTitle: {
    fontSize: 18,
    fontWeight: "600",
    marginTop: 20,
    marginBottom: 10,
    color: "#333",
  },

  ingredientRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 12,
  },

  listItem: {
    flexDirection: "row",
    alignItems: "flex-start",
    marginBottom: 8,
  },

  removeBtn: {
    marginLeft: 8,
    marginTop: 10,
    padding: 6,
  },

  removeText: {
    color: "#e74c3c",
    fontSize: 22,
    fontWeight: "bold",
  },

  addBtn: {
    backgroundColor: "#f5f5f5",
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
    marginBottom: 16,
  },

  addBtnText: {
    color: "#e74c3c",
    fontWeight: "600",
    fontSize: 16,
  },

  buttonRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 30,
    marginBottom: 30,
  },

  cancelBtn: {
    paddingHorizontal: 24,
    paddingVertical: 16,
    justifyContent: "center",
  },

  cancelText: {
    color: "#666",
    fontSize: 16,
    fontWeight: "600",
  },

  saveBtn: {
    backgroundColor: "#e74c3c",
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 12,
  },

  saveText: {
    color: "#fff",
    fontWeight: "700",
    fontSize: 16,
  },
});

export default AddRecipeModal;