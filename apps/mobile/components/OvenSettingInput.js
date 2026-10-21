import React from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Image,
  StyleSheet,
} from "react-native";
import { OVEN_MODES, getOvenModeIcon } from "../assets/icons";

const OvenSettingInput = ({
  temperature,
  mode,
  onTemperatureChange,
  onModeChange,
}) => {
  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        placeholder="Oven temperature (°C)"
        keyboardType="number-pad"
        returnKeyType="done"
        value={temperature || ""}
        onChangeText={onTemperatureChange}
      />

      <View style={styles.modes}>
        {OVEN_MODES.map(option => {
          const active = (mode ?? null) === option.value;

          return (
            <TouchableOpacity
              key={option.label}
              style={[styles.mode, active && styles.modeActive]}
              onPress={() => onModeChange(option.value)}
              activeOpacity={0.8}
            >
              <Image
                source={getOvenModeIcon(option.value)}
                style={styles.icon}
              />
              <Text style={[styles.label, active && styles.labelActive]}>
                {option.label}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    gap: 8,
    marginBottom: 12,
  },
  input: {
    backgroundColor: "#fff",
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  modes: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  mode: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: "#e5e5e5",
    backgroundColor: "#f5f5f5",
  },
  modeActive: {
    backgroundColor: "#fff5f4",
    borderColor: "#e74c3c",
  },
  icon: {
    width: 18,
    height: 18,
  },
  label: {
    color: "#555",
    fontSize: 13,
  },
  labelActive: {
    color: "#e74c3c",
    fontWeight: "600",
  },
});

export default OvenSettingInput;
