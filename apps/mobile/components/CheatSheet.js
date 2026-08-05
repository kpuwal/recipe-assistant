import React from "react";
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";

const CheatSheet = ({ onSync }) => {
  const [syncing, setSyncing] = React.useState(false);

  const tips = [
    {
      icon: "search",
      title: "Normaal zoeken",
      examples: ["pasta", "kip met rijst", "onder 20 min"],
    },
    {
      icon: "information-circle",
      title: "Kennisvragen",
      examples: [
        "hoe kook ik rijst?",
        "wat is falafel?",
        "hoeveel gram is 1 el?",
      ],
    },
    {
      icon: "restaurant",
      title: "AI recepten (restjes)",
      examples: [
        "ik heb kip en broccoli",
        "wat kan ik maken met restjes?",
        "maak iets met courgette",
      ],
    },
  ];

  const handleSync = async () => {
    if (syncing) return;

    try {
      setSyncing(true);
      await onSync();
    } catch (error) {
      console.error("Sync error:", error);
    } finally {
      setSyncing(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.tipsList}
        contentContainerStyle={styles.tipsContent}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        {tips.map((tip, index) => (
          <View key={index} style={styles.tipRow}>
            <Ionicons name={tip.icon} size={26} color="#e74c3c" style={styles.icon} />

            <View style={styles.tipContent}>
              <Text style={styles.tipTitle}>{tip.title}</Text>
              {tip.examples.map((example, i) => (
                <Text key={i} style={styles.example}>
                  • {example}
                </Text>
              ))}
            </View>
          </View>
        ))}

        {/* Sync button lives in the scrollable flow so it moves naturally
            with the content when the keyboard compresses the view. */}
        <TouchableOpacity
          style={[styles.syncButton, syncing && styles.syncButtonDisabled]}
          disabled={syncing}
          onPress={handleSync}
          activeOpacity={0.8}
        >
          <Ionicons
            name={syncing ? "hourglass-outline" : "sync-outline"}
            size={22}
            color="#fff"
          />
          <Text style={styles.syncButtonText}>
            {syncing ? "Synchroniseren..." : "Recepten synchroniseren"}
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: "#f8f9fa",
  },
  tipsList: {
    flex: 1,
  },
  tipsContent: {
    paddingBottom: 20,
  },
  tipRow: {
    flexDirection: "row",
    marginBottom: 24,
  },
  icon: {
    marginRight: 16,
    marginTop: 4,
  },
  tipContent: {
    flex: 1,
  },
  tipTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: "#222",
    marginBottom: 2,
  },
  example: {
    fontSize: 15,
    color: "#555",
    marginVertical: 2,
  },
  syncButton: {
    marginTop: 20,
    backgroundColor: "#e74c3c",
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 25,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
  },
  syncButtonDisabled: {
    opacity: 0.65,
  },
  syncButtonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
    marginLeft: 8,
  },
});

export default CheatSheet;
