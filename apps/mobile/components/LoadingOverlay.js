import React from "react";
import {
  View,
  ActivityIndicator,
  Text,
  StyleSheet,
  Image,
} from "react-native";

export default function LoadingOverlay({
  message = "Chinchilla denkt na...",
}) {
  return (
    <View style={styles.overlay}>
      <View style={styles.card}>
        <View style={styles.left}>
          <View style={styles.loadingRow}>
            <ActivityIndicator size="small" color="#E74C3C" />
          </View>
          <Text style={styles.text}>Chinchilla</Text>
          <Text style={styles.text}>denkt na...</Text>
        </View>
        <Image
          source={require("../assets/thinking.jpg")}
          style={styles.image}
          resizeMode="contain"
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "rgba(0,0,0,0.35)",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 9999,
    elevation: 9999,
  },

  card: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#f9f9f9",
    borderRadius: 20,
    padding: 20,
    width: "65%",
    maxWidth: 280,

    elevation: 8,
    shadowColor: "#000",
    shadowOpacity: 0.2,
    shadowRadius: 10,
    shadowOffset: {
      width: 0,
      height: 4,
    },
  },

  left: {
    flex: 1,
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    paddingRight: 0,
  },

  image: {
    width: 80,
    height: 140,
    // borderRadius: 12,
  },


  loadingRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
  },

  text: {
    marginLeft: 0,
    fontSize: 22,
    fontWeight: "600",
    color: "#444444",
  },
});