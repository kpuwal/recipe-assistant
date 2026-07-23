import React from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const CheatSheet = ({ onClose, onSync }) => {
  const [syncing, setSyncing] = React.useState(false);

  const tips = [
    {
      icon: "search",
      title: "Normaal zoeken",
      examples: ["pasta", "kip met rijst", "onder 20 min"]
    },
    {
      icon: "information-circle",
      title: "Kennisvragen",
      examples: ["hoe kook ik rijst?", "wat is falafel?", "hoeveel gram is 1 el?"]
    },
    // {
    //   icon: "swap-horizontal",
    //   title: "Vervangers vragen",
    //   examples: ["vervang kaas", "alternatief voor ei", "in plaats van bacon"]
    // },
    {
      icon: "restaurant",
      title: "AI recepten (restjes)",
      examples: ["ik heb kip en broccoli", "wat kan ik maken met restjes?", "maak iets met courgette"]
    },
  ];

  return (
    <View style={styles.container}>
      <ScrollView style={styles.tipsList} showsVerticalScrollIndicator={false}>
        {tips.map((tip, index) => (
          <View key={index} style={styles.tipRow}>
            <Ionicons name={tip.icon} size={26} color="#e74c3c" style={styles.icon} />
            <View style={styles.tipContent}>
              <Text style={styles.tipTitle}>{tip.title}</Text>
              {tip.examples.map((ex, i) => (
                <Text key={i} style={styles.example}>• {ex}</Text>
              ))}
            </View>
          </View>
        ))}
      </ScrollView>

      <TouchableOpacity
        style={styles.syncButton}
        disabled={syncing}
        onPress={async () => {
          setSyncing(true);
          await onSync();
          setSyncing(false);
        }}
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
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: "#f8f9fa",
    justifyContent: "center",
  },
  tipsList: {
    flex: 1,
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
    marginTop: 10,
    backgroundColor: "#e74c3c",
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 25,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
  },

  syncButtonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
    marginLeft: 8,
  },
});

export default CheatSheet;