// components/RecipeCard.js
import React, { useMemo, memo } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Image } from 'expo-image';
import { Ionicons } from '@expo/vector-icons';
import { buildRecipeImageUrl } from '../services/api';

const RecipeCard = memo(({ recipe, onPress, onDelete, API_URL }) => {
  const imageUri = useMemo(
    () => buildRecipeImageUrl(recipe.source, recipe.image, 300),
    [recipe.source, recipe.image]
  );

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
      {imageUri ? (
        <Image
          source={imageUri}
          style={styles.recipeThumbnail}
          contentFit="cover"
          cachePolicy="memory-disk"
          recyclingKey={imageUri.uri}
          transition={150}
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
              <Ionicons name="trash-outline" size={22} color="#be123c" />
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
  )
});

const styles = StyleSheet.create({
  recipeCard: {
    flexDirection: "row",
    borderRadius: 18,
    overflow: "hidden",
    marginTop: 12,
    backgroundColor: "#fff",
    marginHorizontal: 4,
    elevation: 1,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    borderWidth: 1,
    borderColor: "#f0f0f0",
  },
  actionButtonsRow: {
    flexDirection: "column",
    position: "absolute",
    bottom: 8,
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
    backgroundColor: "#fafafa",
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