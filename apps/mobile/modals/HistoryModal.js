import React, { useCallback, useEffect, useState } from "react";
import {
  View,
  Text,
  Modal,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  StyleSheet,
} from "react-native";
import { Image } from "expo-image";
import { Ionicons } from "@expo/vector-icons";

import apiService, { buildRecipeImageUrl } from "../services/api";
import { formatCookedDate } from "../utils/dates";

const HistoryModal = ({ visible, onClose, onSelectRecipe }) => {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(false);
    try {
      const response = await apiService.getHistory();
      setEntries(response.data || []);
    } catch (err) {
      console.error("History load error:", err);
      setError(true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (visible) {
      load();
    }
  }, [visible, load]);

  const renderItem = useCallback(
    ({ item }) => {
      const imageSource = buildRecipeImageUrl(item.source, item.image, 120);

      return (
        <TouchableOpacity
          style={styles.row}
          activeOpacity={0.85}
          onPress={() => onSelectRecipe?.(item)}
        >
          {imageSource ? (
            <Image
              source={imageSource}
              style={styles.thumb}
              contentFit="cover"
              cachePolicy="memory-disk"
              transition={150}
            />
          ) : (
            <View style={[styles.thumb, styles.thumbPlaceholder]}>
              <Text style={styles.thumbPlaceholderText}>🍳</Text>
            </View>
          )}

          <View style={styles.rowInfo}>
            <Text style={styles.rowDate}>{formatCookedDate(item.date)}</Text>
            <Text style={styles.rowTitle} numberOfLines={2}>
              {item.title}
            </Text>
          </View>
        </TouchableOpacity>
      );
    },
    [onSelectRecipe]
  );

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={false}
      onRequestClose={onClose}
    >
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Ionicons name="close" size={28} color="#333" />
          </TouchableOpacity>
          <Text style={styles.title}>Kookgeschiedenis</Text>
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color="#e74c3c" />
          </View>
        ) : error ? (
          <View style={styles.center}>
            <Text style={styles.emptyText}>
              Kon geschiedenis niet laden.
            </Text>
            <TouchableOpacity style={styles.retryButton} onPress={load}>
              <Text style={styles.retryText}>Opnieuw proberen</Text>
            </TouchableOpacity>
          </View>
        ) : entries.length === 0 ? (
          <View style={styles.center}>
            <Text style={styles.emptyText}>
              Nog niets gekookt. Druk op "TODAY" bij een recept.
            </Text>
          </View>
        ) : (
          <FlatList
            data={entries}
            keyExtractor={(item) => `${item.date}-${item.recipe_id}`}
            renderItem={renderItem}
            contentContainerStyle={styles.listContent}
          />
        )}
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
    flexDirection: "row",
    alignItems: "center",
    paddingTop: 50,
    paddingBottom: 15,
    paddingHorizontal: 20,
    backgroundColor: "#fff",
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
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
  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 30,
  },
  emptyText: {
    fontSize: 16,
    color: "#777",
    textAlign: "center",
    lineHeight: 22,
  },
  retryButton: {
    marginTop: 16,
    paddingHorizontal: 20,
    paddingVertical: 10,
    backgroundColor: "#e74c3c",
    borderRadius: 999,
  },
  retryText: {
    color: "#fff",
    fontWeight: "600",
  },
  listContent: {
    padding: 12,
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#fff",
    borderRadius: 14,
    padding: 10,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: "#f0f0f0",
    elevation: 1,
  },
  thumb: {
    width: 56,
    height: 56,
    borderRadius: 10,
    backgroundColor: "#f0f0f0",
  },
  thumbPlaceholder: {
    justifyContent: "center",
    alignItems: "center",
  },
  thumbPlaceholderText: {
    fontSize: 24,
  },
  rowInfo: {
    flex: 1,
    marginLeft: 12,
  },
  rowDate: {
    fontSize: 13,
    fontWeight: "700",
    color: "#e74c3c",
    marginBottom: 2,
  },
  rowTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#1a1a1a",
  },
});

export default HistoryModal;
