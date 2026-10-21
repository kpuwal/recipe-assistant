import React from "react";
import { View, Text, TouchableOpacity, StyleSheet, Image } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { formatTime } from "../../utils/formatTime";
import { getRemainingMs } from "../../hooks/useTimers";
import { getTimerIcon } from "../../assets/icons";
import { DEFAULT_TIMER_COLOR } from "../../constants/timerColors";

const TimerCard = ({ timer, now, onToggle, onStop }) => {
  const isDone = timer.status === "done";
  const isPaused = timer.status === "paused";
  const remaining = getRemainingMs(timer, now);
  const iconSource = getTimerIcon(timer.icon);

  const handlePress = () => {
    if (isDone) {
      onStop(timer.id);
    } else {
      onToggle(timer.id);
    }
  };

  return (
    <View
      style={[
        styles.card,
        { backgroundColor: timer.color || DEFAULT_TIMER_COLOR },
        isPaused && styles.cardPaused,
        isDone && styles.cardDone,
      ]}
    >
      <TouchableOpacity
        style={styles.main}
        activeOpacity={0.85}
        onPress={handlePress}
      >
        <View style={styles.iconWrap}>
          {iconSource ? (
            <Image
              source={iconSource}
              style={styles.iconImage}
              resizeMode="contain"
            />
          ) : (
            <Ionicons name="timer-outline" size={16} color="#fff" />
          )}
        </View>
        <View style={styles.textCol}>
          <Text style={styles.label} numberOfLines={1}>
            {timer.label}
          </Text>
          <Text style={styles.time}>
            {isDone ? "Klaar" : formatTime(remaining)}
          </Text>
        </View>
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.stop}
        onPress={() => onStop(timer.id)}
        hitSlop={8}
      >
        <Ionicons name="close" size={14} color="#fff" />
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    width: 134,
    borderRadius: 12,
    backgroundColor: "#e74c3c",
    paddingVertical: 8,
    paddingHorizontal: 10,
    marginBottom: 10,
    shadowColor: "#000",
    shadowOpacity: 0.25,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 2 },
    elevation: 5,
  },

  cardPaused: {
    backgroundColor: "#f39c12",
  },

  cardDone: {
    backgroundColor: "#16a34a",
  },

  main: {
    flexDirection: "row",
    alignItems: "center",
  },

  iconWrap: {
    width: 30,
    height: 30,
    alignItems: "center",
    justifyContent: "center",
    marginRight: 6,
  },

  iconImage: {
    width: 28,
    height: 28,
  },

  textCol: {
    flex: 1,
    alignItems: "center",
    paddingRight: 2,
  },

  label: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "600",
    maxWidth: "100%",
  },

  time: {
    color: "#fff",
    fontSize: 24,
    fontWeight: "700",
    fontVariant: ["tabular-nums"],
    marginTop: 2,
  },

  stop: {
    position: "absolute",
    top: 2,
    right: 2,
    padding: 2,
  },
});

export default React.memo(TimerCard);
