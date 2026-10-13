import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const ActionBar = ({ onClear, onSync }) => {
  const [syncing, setSyncing] = useState(false);

  const handleSync = async () => {
    if (syncing) return;
    try {
      setSyncing(true);
      await onSync?.();
    } catch (error) {
      console.error("Sync error:", error);
    } finally {
      setSyncing(false);
    }
  };

  return (
    <View style={styles.bar}>
      <TouchableOpacity
        style={[styles.pillButton, syncing && styles.pillButtonDisabled]}
        onPress={handleSync}
        disabled={syncing}
        activeOpacity={0.8}
      >
        <Ionicons
          name={syncing ? "hourglass-outline" : "sync-outline"}
          size={18}
          color="#ef4444"
        />
        <Text style={[styles.pillText, styles.syncText]}>Sync</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.pillButton}
        onPress={onClear}
        activeOpacity={0.8}
      >
        <Text style={styles.pillText}>✕ Clear</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  bar: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "flex-start",
    paddingHorizontal: 16,
    paddingVertical: 8,
    gap: 8,
    backgroundColor: "#fff",
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
  },
  pillButton: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 14,
    paddingVertical: 7,
    backgroundColor: "#fee2e2",
    borderRadius: 999,
    borderWidth: 1,
    borderColor: "#fca5a5",
    minHeight: 36,
    justifyContent: "center",
  },
  pillButtonDisabled: {
    opacity: 0.6,
  },
  pillText: {
    fontSize: 15,
    fontWeight: "600",
    color: "#ef4444",
    lineHeight: 18,
  },
  syncText: {
    marginLeft: 8,
  },
});

export default ActionBar;
