import React, { useCallback } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Modal,
  Keyboard,
  TouchableWithoutFeedback,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { KeyboardAwareScrollView } from "react-native-keyboard-aware-scroll-view";
import { Ionicons } from "@expo/vector-icons";
import apiService from "../services/api";
import useRecipeForm from "../hooks/useRecipeForm";

const EditRecipeModal = ({ visible, recipe, onClose, onRecipeUpdated }) => {
  const handleUpdate = useCallback(
    async recipeData => {
      if (!recipe?.id) return;
      return apiService.updateRecipe(recipe.id, { ...recipeData, id: recipe.id });
    },
    [recipe?.id]
  );

  const handleSuccess = useCallback(
    response => {
      onRecipeUpdated?.(response.data);
      onClose();
    },
    [onClose, onRecipeUpdated]
  );

  const { form, submitting, handleSubmit, updateField, updateIngredient, addIngredient, removeIngredient, addStep, removeStep } =
    useRecipeForm({
      initialValues: recipe,
      onSubmit: handleUpdate,
      onSuccess: handleSuccess,
    });

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
              <Text style={styles.title}>Edit Recipe</Text>
            </View>

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
            {form.ingredients.map((ing, index) => (
              <View key={index} style={styles.ingredientRow}>
                <TextInput
                  style={[styles.input, { flex: 2 }]}
                  placeholder="Quantity"
                  value={ing.quantity}
                  onChangeText={v => updateIngredient(index, "quantity", v)}
                />
                <TextInput
                  style={[styles.input, { flex: 3 }]}
                  placeholder="Ingredient name *"
                  value={ing.name}
                  onChangeText={v => updateIngredient(index, "name", v)}
                />
                <TouchableOpacity onPress={() => removeIngredient(index)} style={styles.removeBtn}>
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
                  placeholder={`Step ${index + 1}`}
                  multiline
                  textAlignVertical="top"
                  value={step}
                  onChangeText={v => {
                    const newSteps = [...form.steps];
                    newSteps[index] = v;
                    updateField("steps", newSteps);
                  }}
                />
                <TouchableOpacity onPress={() => removeStep(index)} style={styles.removeBtn}>
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
              <TouchableOpacity
                style={[styles.saveBtn, submitting && styles.saveBtnDisabled]}
                onPress={handleSubmit}
                disabled={submitting}
              >
                <Text style={[styles.saveText, submitting && styles.saveTextDisabled]}>
                  Save Changes
                </Text>
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
  saveBtnDisabled: { opacity: 0.5 },
  saveText: { color: "#fff", fontWeight: "700", fontSize: 16 },
  saveTextDisabled: { opacity: 0.7 },
});

export default EditRecipeModal;
