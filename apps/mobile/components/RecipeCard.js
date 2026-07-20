// components/RecipeCard.js
import React from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const RecipeCard = ({ recipe, onPress, onDelete, API_URL }) => {
  const handleDelete = (e) => {
    e.stopPropagation();
    onDelete(recipe.id);
  };

  return (
    <TouchableOpacity 
      style={styles.recipeCard} 
      onPress={() => onPress(recipe)} 
      activeOpacity={0.9}
    >
      {recipe.image ? (
        <Image 
          source={{ uri: `${API_URL}/images/${recipe.source}/${recipe.image}` }} 
          style={styles.recipeThumbnail} 
          resizeMode="cover" 
        />
      ) : (
        <View style={styles.placeholderImage}>
          <Text style={styles.placeholderText}>🍳</Text>
        </View>
      )}

      <View style={styles.recipeInfo}>
        <View style={styles.actionButtonsRow}>
          {recipe.source === "personal" && (
            <TouchableOpacity 
              style={styles.deleteButton} 
              onPress={handleDelete}
            >
              <Ionicons name="trash-outline" size={22} color="#d9534f" />
            </TouchableOpacity>
          )}
        </View>

        <Text style={styles.recipeTitle} numberOfLines={2}>
          {recipe.title}
        </Text>

        <View style={styles.metaRow}>
          {recipe.time_minutes && (
            <Text style={styles.recipeMeta}>⏱ {recipe.time_minutes} min</Text>
          )}
          {recipe.persons && (
            <Text style={styles.recipeMeta}>👥 {recipe.persons} pers.</Text>
          )}
        </View>
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  recipeCard: {
    flexDirection: "row",
    borderRadius: 18,
    overflow: "hidden",
    marginTop: 12,
    backgroundColor: "#fff",
    marginHorizontal: 4,
    elevation: 4,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.12,
    shadowRadius: 6,
    borderWidth: 1,
    borderColor: "#f0f0f0",
  },
  actionButtonsRow: {
    flexDirection: "column",
    position: "absolute",
    top: 8,
    right: 8,
    zIndex: 10,
  },
  deleteButton: {
    padding: 6,
  },
  recipeThumbnail: {
    width: 90,
    height: 90,
  },
  placeholderImage: {
    width: 90,
    height: 90,
    backgroundColor: "#f8f9fa",
    justifyContent: "center",
    alignItems: "center",
    borderRightWidth: 1,
    borderRightColor: "#f0f0f0",
  },
  placeholderText: {
    fontSize: 32,
  },
  recipeInfo: {
    flex: 1,
    paddingHorizontal: 14,
    paddingVertical: 10,
    justifyContent: "center",
  },
  recipeTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#1a1a1a",
    lineHeight: 20,
    marginBottom: 4,
  },
  metaRow: {
    flexDirection: "row",
    gap: 8,
  },
  recipeMeta: {
    fontSize: 14,
    color: "#555",
  },
});

export default RecipeCard;