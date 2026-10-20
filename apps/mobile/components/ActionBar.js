import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const ActionBar = ({ onClear, onSync, onHistory }) => {
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
        style={[styles.pillButton, styles.historyButton]}
        onPress={onHistory}
        activeOpacity={0.8}
        hitSlop={8}
      >
        <Ionicons name="time-outline" size={15} color="#b45309" />
        <Text style={[styles.pillText, styles.iconLabel, styles.historyText]}>
          History
        </Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={[
          styles.pillButton,
          styles.syncButton,
          syncing && styles.pillButtonDisabled,
        ]}
        onPress={handleSync}
        disabled={syncing}
        activeOpacity={0.8}
        hitSlop={8}
      >
        <Ionicons
          name={syncing ? "hourglass-outline" : "sync-outline"}
          size={15}
          color="#0369a1"
        />
        <Text style={[styles.pillText, styles.iconLabel, styles.syncText]}>
          Sync
        </Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={[styles.pillButton, styles.clearButton]}
        onPress={onClear}
        activeOpacity={0.8}
        hitSlop={8}
      >
        <Text style={[styles.pillText, styles.clearText]}>✕ Clear</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  bar: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "flex-start",
    paddingHorizontal: 14,
    paddingVertical: 6,
    gap: 6,
    backgroundColor: "#fff",
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
  },
  pillButton: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 11,
    paddingVertical: 4,
    borderRadius: 999,
    borderWidth: 1,
    minHeight: 30,
    justifyContent: "center",
  },
  pillButtonDisabled: {
    opacity: 0.6,
  },
  pillText: {
    fontSize: 13,
    fontWeight: "600",
    lineHeight: 16,
  },
  iconLabel: {
    marginLeft: 6,
  },
  historyButton: {
    backgroundColor: "#fef3c7",
    borderColor: "#fcd34d",
  },
  historyText: {
    color: "#b45309",
  },
  syncButton: {
    backgroundColor: "#e0f2fe",
    borderColor: "#7dd3fc",
  },
  syncText: {
    color: "#0369a1",
  },
  clearButton: {
    backgroundColor: "#fee2e2",
    borderColor: "#fca5a5",
  },
  clearText: {
    color: "#be123c",
  },
});

export default ActionBar;
