import React from 'react';
import { ScrollView, TouchableOpacity, Text, StyleSheet } from 'react-native';
import { TAGS } from '../constants/tags';

const TagFilters = ({ activeTag, onTagPress, onAddRecipe, onClear }) => {
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

      {TAGS.map((tag) => (
        <TouchableOpacity 
          key={tag.label} 
          style={[
            styles.tagButton, 
            activeTag === tag.label && styles.tagButtonActive
          ]} 
          onPress={() => onTagPress(tag)}
        >
          <Text style={styles.tagEmoji}>{tag.label.split(' ')[0]}</Text>
          <Text style={styles.tagText}>
            {tag.label.split(' ').slice(1).join(' ')}
          </Text>
        </TouchableOpacity>
      ))}

      <TouchableOpacity style={styles.clearButton} onPress={onClear}>
        <Text style={styles.clearText}>✕ Clear</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  tagsScroll: { maxHeight: 52, backgroundColor: "#fff", borderBottomWidth: 1, borderBottomColor: "#eee" },
  tagsContainer: { flexDirection: "row", alignItems: "center", paddingHorizontal: 16, paddingVertical: 0, gap: 8 },
  tagButton: { flexDirection: "row", paddingHorizontal: 16, paddingVertical: 8, backgroundColor: "#f5f5f5", borderRadius: 999, borderWidth: 1, borderColor: "#e5e5e5", minHeight: 38, justifyContent: "center", alignItems: "center" },
  tagText: { fontSize: 15, fontWeight: "600", color: "#333", textAlign: "center", lineHeight: 18 },
  tagEmoji: { fontSize: 22, lineHeight: 26 },
  tagButtonActive: { backgroundColor: "#e74c3c", borderColor: "#e74c3c" },
  tagTextActive: { color: "#fff" },
  addRecipeButton: { paddingHorizontal: 16, paddingVertical: 8, backgroundColor: "#e74c3c", borderRadius: 999, marginRight: 8, minHeight: 38, justifyContent: "center", alignItems: "center" },
  addRecipeButtonText: { color: "#fff", fontWeight: "600" },
  clearButton: { paddingHorizontal: 14, paddingVertical: 7, backgroundColor: "#fee2e2", borderRadius: 999, borderWidth: 1, borderColor: "#fca5a5", marginLeft: 4, minHeight: 38, justifyContent: "center", alignItems: "center" },
  clearText: { fontSize: 15, fontWeight: "600", color: "#ef4444", textAlign: "center", lineHeight: 18 },
});

export default TagFilters;