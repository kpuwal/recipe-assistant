import React from 'react';
import { ScrollView, TouchableOpacity, Text, StyleSheet } from 'react-native';
import { FILTERS } from '../constants/filters';

const TagFilters = ({ activeFilter, onFilterPress, onAddRecipe }) => {
  return (
    <ScrollView 
      horizontal 
      showsHorizontalScrollIndicator={false} 
      style={styles.tagsScroll}
      contentContainerStyle={styles.tagsContainer}
    >
      <TouchableOpacity style={styles.addRecipeButton} onPress={onAddRecipe}>
        <Text style={styles.addRecipeButtonText}>+ Nieuw Recept</Text>
      </TouchableOpacity>

      {FILTERS.map((filter) => (
        <TouchableOpacity 
          key={filter.id} 
          style={[
            styles.tagButton, 
            activeFilter === filter.id && styles.tagButtonActive
          ]} 
          onPress={() => onFilterPress(filter)}
        >
          <Text style={styles.tagEmoji}>{filter.emoji}</Text>
          <Text
            style={[
              styles.tagText,
              activeFilter === filter.id && styles.tagTextActive,
            ]}
          >
            {filter.label}
          </Text>
        </TouchableOpacity>
      ))}

    </ScrollView>
  );
};

const styles = StyleSheet.create({
  tagsScroll: { maxHeight: 52, backgroundColor: "#fff", borderBottomWidth: 1, borderBottomColor: "#eee" },
  tagsContainer: { flexDirection: "row", alignItems: "center", paddingHorizontal: 16, paddingVertical: 0, gap: 8 },
  tagButton: { flexDirection: "row", paddingHorizontal: 10, paddingVertical: 4, backgroundColor: "#f5f5f5", borderRadius: 999, borderWidth: 1, borderColor: "#e5e5e5", minHeight: 30, justifyContent: "center", alignItems: "center" },
  tagText: { fontSize: 13, fontWeight: "600", color: "#333", textAlign: "center", lineHeight: 16 },
  tagEmoji: { fontSize: 16, lineHeight: 20 },
  tagButtonActive: { backgroundColor: "#e74c3c", borderColor: "#e74c3c" },
  tagTextActive: { color: "#fff" },
  addRecipeButton: { paddingHorizontal: 16, paddingVertical: 8, backgroundColor: "#e74c3c", borderRadius: 999, marginRight: 8, minHeight: 38, justifyContent: "center", alignItems: "center" },
  addRecipeButtonText: { color: "#fff", fontWeight: "600" },
});

export default TagFilters;