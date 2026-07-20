import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  Modal,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Image,
  Alert,
} from "react-native";
import { Ionicons, Entypo, MaterialIcons } from "@expo/vector-icons";
import axios from "axios";

const RecipeModal = ({ visible, recipe, api_url, onClose, onFavoriteChanged, onEditPress, onRecipeSaved }) => {
  const [isFavorite, setIsFavorite] = useState(false);
  const [displayRecipe, setDisplayRecipe] = useState(null);
  const [selectedPersons, setSelectedPersons] = useState(4);
  const [loading, setLoading] = useState(false);
  const [scaling, setScaling] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (recipe) {
      setIsFavorite(recipe.is_favorite ?? false);
      setDisplayRecipe(recipe);
      setSelectedPersons(recipe.persons || 4);
    } else {
      // Reset when no recipe
      setDisplayRecipe(null);
    }
  }, [recipe]);

  const handleSaveAsPersonalRecipe = async () => {
    if (!displayRecipe || saving) return;

    setSaving(true);
    try {
      const recipeToSave = {
        title: displayRecipe.title,
        source: "personal",
        persons: displayRecipe.persons || selectedPersons,
        time_minutes: displayRecipe.time_minutes,
        category: displayRecipe.category || "other",
        ingredients: displayRecipe.ingredients || [],
        steps: displayRecipe.steps || [],
        tips: displayRecipe.tips || null,
        image: null, // AI recipes usually have null image
      };

      const response = await axios.post(`${api_url}/recipes/`, recipeToSave);

      onRecipeSaved?.(response.data);
      onClose();

    } catch (error) {
      console.error("Save recipe error:", error);
      Alert.alert("Error", "Could not save recipe. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const toggleFavorite = async () => {
    if (loading) return;
    
    setLoading(true);
    try {
      const response = await axios.put(`${api_url}/recipes/${recipe.id}/favorite`);
      
      const updatedRecipe = response.data;
      setIsFavorite(updatedRecipe.is_favorite);

      // Notify parent component so list can update too
      onFavoriteChanged?.(updatedRecipe);

    } catch (error) {
      console.error("Toggle favorite error:", error);
      Alert.alert("Fout", "Kon favoriet status niet updaten");
    } finally {
      setLoading(false);
    }
  };

  const scaleRecipe = async (persons) => {
    if (persons === selectedPersons) return;

    if (persons === recipe.persons) {
      setDisplayRecipe(recipe);
      setSelectedPersons(persons);
      return;
    }

    try {
      setScaling(true);
      const response = await axios.get(
        `${api_url}/recipes/${recipe.id}/scale`,
        {
          params: { persons },
        }
      );

      setDisplayRecipe(response.data);
      setSelectedPersons(persons);

    } catch (err) {
      Alert.alert("Fout", "Kon recept niet aanpassen.");
    } finally {
      setScaling(false);
    }
  };

  const handleEdit = () => {
    if (recipe) {
      onEditPress?.(recipe);
    }
  };

  if (!visible || !recipe) {
    return null;
  }

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={false}
      onRequestClose={onClose}
    >
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Ionicons name="close" size={28} color="#333" />
          </TouchableOpacity>

          <Text style={styles.title} numberOfLines={1}>
            {recipe.title}
          </Text>

           {/* Edit Button */}
          {/* {recipe.source === "personal" && ( */}
            <TouchableOpacity 
              onPress={handleEdit}
              style={styles.headerButton}
            >
              <Entypo name="edit" size={24} color="#1e90ff" />
            </TouchableOpacity>
          {/* )} */}

          {/* Save Button - Only for AI Recipes */}
          {recipe.source === "ai" && (
            <TouchableOpacity 
              onPress={handleSaveAsPersonalRecipe}
              disabled={saving}
              style={styles.saveButton}
            >
              <MaterialIcons 
                name="save" 
                size={26} 
                color={saving ? "#999" : "#4CAF50"} 
              />
            </TouchableOpacity>
          )}

          {recipe.source !== "ai" && (
            <TouchableOpacity 
              onPress={toggleFavorite} 
              disabled={loading}
              style={styles.favoriteButton}
            >
              <Ionicons
                name={isFavorite ? "heart" : "heart-outline"}
                size={28}
                color={isFavorite ? "#e74c3c" : "#666"}
              />
            </TouchableOpacity>
          )}
        </View>

        <ScrollView style={styles.scrollContainer} showsVerticalScrollIndicator={false}>
          {/* Recipe Image */}
          {recipe.image && (
            <Image
              source={{ uri: `${api_url}/images/${recipe.source}/${recipe.image}` }}
              style={styles.recipeImage}
              resizeMode="cover"
            />
          )}

          {/* Meta Info */}
          <View style={styles.metaContainer}>
            <View style={styles.scaleContainer}>
              <Ionicons name="people-outline" size={20} color="#555" />
              <Text style={styles.scaleTitle}>Personen</Text>
              
              <View style={styles.scaleButtons}>
                {[2, 4].map((p) => (
                  <TouchableOpacity
                    key={p}
                    onPress={() => scaleRecipe(p)}
                    style={[
                      styles.personButton,
                      selectedPersons === p && styles.personButtonSelected,
                    ]}
                  >
                    <Text
                      style={[
                        styles.personText,
                        selectedPersons === p && styles.personTextSelected,
                      ]}
                    >
                      {p}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            {recipe.time_minutes && (
              <View style={styles.infoRow}>
                <Ionicons name="time-outline" size={20} color="#555" />
                <Text style={styles.infoText}>
                  {recipe.time_minutes} minuten
                </Text>
              </View>
            )}

            {recipe.category && recipe.category !== "other" && (
              <View style={styles.infoRow}>
                <Ionicons name="pricetag-outline" size={20} color="#555" />
                <Text style={styles.infoText}>{recipe.category}</Text>
              </View>
            )}
          </View>

          {/* Ingredients */}
          <Text style={styles.sectionTitle}>Ingrediënten</Text>
          <View style={styles.ingredientsContainer}>
            {displayRecipe?.ingredients?.map((item, index) => (
              <View key={index} style={styles.ingredientRow}>
                <Text style={styles.quantity}>{item.quantity || ""}</Text>
                <Text style={styles.ingredientName}>{item.name}</Text>
              </View>
            ))}
          </View>

          {/* Steps */}
          <Text style={styles.sectionTitle}>Bereiding</Text>
          {recipe.steps?.map((step, index) => (
            <View key={index} style={styles.stepContainer}>
              <Text style={styles.stepNumber}>{index + 1}</Text>
              <Text style={styles.stepText}>{step}</Text>
            </View>
          ))}

          {/* Tips */}
          {recipe.tips && recipe.tips.length > 0 && (
            <>
              <Text style={styles.sectionTitle}>Tips</Text>
              <View style={styles.tipsContainer}>
                <Text style={styles.tipsText}>{recipe.tips}</Text>
              </View>
            </>
          )}
        </ScrollView>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f8f9fa",
  },

  header: {
    backgroundColor: "#fff",
    paddingTop: 50,
    paddingBottom: 15,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
    flexDirection: "row",
    alignItems: "center",
  },

  closeButton: {
    marginRight: 15,
  },

  title: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#1a1a1a",
    flex: 1,
  },

  favoriteButton: {
    padding: 8,
  },

  scrollContainer: {
    flex: 1,
  },

  recipeImage: {
    width: "100%",
    height: 260,
    backgroundColor: "#eee",
  },

  metaContainer: {
    flexDirection: "row",
    flexWrap: "wrap",
    padding: 20,
    gap: 12,
    backgroundColor: "#fff",
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
  },

  scaleContainer: {
    backgroundColor: "#fff",
    padding: 20,
    alignItems: "center",
    flexDirection: "row",
  },

  scaleTitle: {
    color: "#333",
    fontSize: 16,
    marginLeft: 8,
  },

  scaleButtons: {
    flexDirection: "row",
  },

  personButton: {
    width: 28,
    height: 28,
    borderRadius: 2,
    borderWidth: 1,
    borderColor: "#ddd",
    justifyContent: "center",
    alignItems: "center",
    marginHorizontal: 4,
  },

  personButtonSelected: {
    backgroundColor: "#e74c3c",
    borderColor: "#e74c3c",
  },

  personText: {
    fontWeight: "bold",
    color: "#333",
    fontSize: 16,
  },

  personTextSelected: {
    color: "white",
  },

  infoRow: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#f8f9fa",
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
  },

  infoText: {
    marginLeft: 8,
    fontSize: 16,
    color: "#333",
  },

  sectionTitle: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#1a1a1a",
    marginTop: 25,
    marginBottom: 12,
    paddingHorizontal: 20,
  },

  ingredientsContainer: {
    backgroundColor: "#fff",
    paddingHorizontal: 20,
    paddingVertical: 15,
  },

  ingredientRow: {
    flexDirection: "row",
    paddingVertical: 9,
    borderBottomWidth: 1,
    borderBottomColor: "#f0f0f0",
  },

  quantity: {
    width: 90,
    fontWeight: "600",
    color: "#e74c3c",
  },

  ingredientName: {
    flex: 1,
    color: "#333",
    fontSize: 16,
  },

  stepContainer: {
    flexDirection: "row",
    marginBottom: 20,
    backgroundColor: "#fff",
    padding: 18,
    borderRadius: 12,
    marginHorizontal: 20,
  },

  stepNumber: {
    fontWeight: "bold",
    fontSize: 18,
    color: "#e74c3c",
    marginRight: 14,
    width: 26,
  },

  stepText: {
    flex: 1,
    fontSize: 16,
    lineHeight: 24,
    color: "#333",
  },

  tipsContainer: {
    backgroundColor: "#fff3cd",
    marginHorizontal: 20,
    padding: 18,
    borderRadius: 12,
    borderLeftWidth: 5,
    borderLeftColor: "#f4c430",
    marginBottom: 30,
  },

  tipsText: {
    fontSize: 16,
    lineHeight: 24,
    color: "#444",
  },

  saveButton: {
    padding: 8,
    marginLeft: 8,
  },
});

export default RecipeModal;