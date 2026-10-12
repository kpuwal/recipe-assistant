import React from "react";
import { View, StyleSheet } from "react-native";
import { useTimers } from "../../hooks/useTimers";
import TimerCard from "./TimerCard";

const TimerOverlay = () => {
  const { timers, now, toggle, stop } = useTimers();

  if (timers.length === 0) return null;

  return (
    <View style={styles.overlay} pointerEvents="box-none">
      {timers.map((timer) => (
        <TimerCard
          key={timer.id}
          timer={timer}
          now={now}
          onToggle={toggle}
          onStop={stop}
        />
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  overlay: {
    position: "absolute",
    top: 132,
    right: 12,
    alignItems: "flex-end",
    zIndex: 1000,
  },
});

export default TimerOverlay;
