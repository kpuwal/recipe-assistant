import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";

import { CATEGORIES } from "../constants/categories";

const CategoryChips = ({ value, onChange }) => {
  const current = value || "other";
  const known = CATEGORIES.some((category) => category.value === current);
  const options = known
    ? CATEGORIES
    : [{ value: current, label: current, emoji: "🏷️" }, ...CATEGORIES];

  return (
    <View style={styles.wrap}>
      {options.map((category) => {
        const selected = category.value === current;
        return (
          <TouchableOpacity
            key={category.value}
            style={[styles.chip, selected && styles.chipSelected]}
            onPress={() => onChange?.(category.value)}
            activeOpacity={0.8}
            hitSlop={4}
          >
            <Text style={[styles.label, selected && styles.labelSelected]}>
              {category.emoji} {category.label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
};

const styles = StyleSheet.create({
  wrap: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: 12,
  },
  chip: {
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: "#e5e5e5",
    backgroundColor: "#f5f5f5",
  },
  chipSelected: {
    backgroundColor: "#e74c3c",
    borderColor: "#e74c3c",
  },
  label: {
    fontSize: 14,
    fontWeight: "600",
    color: "#333",
  },
  labelSelected: {
    color: "#fff",
  },
});

export default CategoryChips;
