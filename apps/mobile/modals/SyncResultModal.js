import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';

const SyncResultModal = ({ result, onClose }) => {
  if (!result) return null;

  return (
    <View style={styles.syncOverlay}>
      <View style={styles.syncCard}>
        <Text style={styles.syncTitle}>
          <MaterialCommunityIcons name="dropbox" size={30} color="black" />  
          Sync voltooid
        </Text>

        <View style={styles.syncRow}>
          <Ionicons name="checkmark-circle" size={26} color="#2ecc71" />
          <Text style={styles.syncLabel}>Verwerkt</Text>
          <Text style={styles.syncNumber}>{result.processed}</Text>
        </View>

        <View style={styles.syncRow}>
          <Ionicons name="arrow-forward-circle" size={26} color="#f39c12" />
          <Text style={styles.syncLabel}>Overgeslagen</Text>
          <Text style={styles.syncNumber}>{result.skipped}</Text>
        </View>

        <View style={styles.syncRow}>
          <Ionicons name="close-circle" size={26} color="#e74c3c" />
          <Text style={styles.syncLabel}>Mislukt</Text>
          <Text style={styles.syncNumber}>{result.failed}</Text>
        </View>

        <TouchableOpacity
          style={styles.syncCloseButton}
          onPress={onClose}
        >
          <Text style={styles.syncCloseText}>OK</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  syncOverlay: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(0,0,0,0.35)",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 300,
  },

  syncCard: {
    width: "80%",
    backgroundColor: "#fff",
    borderRadius: 20,
    padding: 24,
    elevation: 10,
  },

  syncTitle: {
    fontSize: 22,
    fontWeight: "700",
    textAlign: "center",
    marginBottom: 20,
  },

  syncRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 10,
    gap: 12,
  },

  syncLabel: {
    flex: 1,
    fontSize: 16,
    color: "#444",
  },

  syncNumber: {
    fontSize: 18,
    fontWeight: "700",
  },

  syncCloseButton: {
    marginTop: 20,
    backgroundColor: "#e74c3c",
    borderRadius: 25,
    paddingVertical: 12,
    alignItems: "center",
  },

  syncCloseText: {
    color: "#fff",
    fontWeight: "700",
    fontSize: 16,
  },
});

export default SyncResultModal;