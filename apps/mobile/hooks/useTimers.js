import React, {
  createContext,
  useContext,
  useState,
  useRef,
  useEffect,
  useCallback,
  useMemo,
} from "react";
import { AppState } from "react-native";
import { setAudioModeAsync, useAudioPlayer } from "expo-audio";

const TICK_MS = 250;
const TIMER_ALARM_SOUND = require("../assets/sounds/timer-done.wav");

const TimersContext = createContext(null);

let idCounter = 0;
const nextId = () => `timer-${Date.now()}-${idCounter++}`;

export const getRemainingMs = (timer, now) => {
  if (timer.status === "running" && timer.endsAt != null) {
    return Math.max(0, timer.endsAt - now);
  }
  return timer.remainingMs;
};

export const TimersProvider = ({ children }) => {
  const [timers, setTimers] = useState([]);
  const [now, setNow] = useState(() => Date.now());

  const intervalRef = useRef(null);
  const timersRef = useRef([]);
  const doneTimerIdsRef = useRef(new Set());
  const alarmPlayer = useAudioPlayer(TIMER_ALARM_SOUND);

  useEffect(() => {
    setAudioModeAsync({
      playsInSilentMode: true,
      shouldPlayInBackground: false,
      interruptionMode: "doNotMix",
    }).catch(() => {});
  }, []);

  useEffect(() => {
    const doneIds = new Set(
      timers.filter((timer) => timer.status === "done").map((timer) => timer.id)
    );
    const hasNewDone = [...doneIds].some(
      (id) => !doneTimerIdsRef.current.has(id)
    );
    doneTimerIdsRef.current = doneIds;

    if (!hasNewDone) return;

    alarmPlayer.seekTo(0).then(() => alarmPlayer.play()).catch(() => {});
  }, [timers, alarmPlayer]);

  useEffect(() => {
    timersRef.current = timers;
  }, [timers]);

  const hasRunning = timers.some((t) => t.status === "running");

  useEffect(() => {
    if (!hasRunning) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    intervalRef.current = setInterval(() => {
      setNow(Date.now());
    }, TICK_MS);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [hasRunning]);

  useEffect(() => {
    setTimers((prev) => {
      let changed = false;
      const next = prev.map((timer) => {
        if (
          timer.status === "running" &&
          timer.endsAt != null &&
          now >= timer.endsAt
        ) {
          changed = true;
          return { ...timer, status: "done", endsAt: null, remainingMs: 0 };
        }
        return timer;
      });
      return changed ? next : prev;
    });
  }, [now]);

  useEffect(() => {
    const subscription = AppState.addEventListener("change", (state) => {
      if (state === "active") {
        setNow(Date.now());
      }
    });
    return () => subscription.remove();
  }, []);

  const startTimer = useCallback(({ sourceId = null, label, durationSeconds, icon = null, color = null }) => {
    const exists =
      sourceId && timersRef.current.some((t) => t.sourceId === sourceId);
    if (exists) return false;

    const start = Date.now();
    const timer = {
      id: nextId(),
      sourceId,
      label,
      durationSeconds,
      icon,
      color,
      status: "running",
      endsAt: start + durationSeconds * 1000,
      remainingMs: durationSeconds * 1000,
    };

    setTimers((prev) => {
      if (sourceId && prev.some((t) => t.sourceId === sourceId)) return prev;
      return [...prev, timer];
    });
    setNow(Date.now());
    return true;
  }, []);

  const toggle = useCallback((id) => {
    setTimers((prev) =>
      prev.map((timer) => {
        if (timer.id !== id) return timer;

        if (timer.status === "running") {
          return {
            ...timer,
            status: "paused",
            endsAt: null,
            remainingMs: Math.max(0, timer.endsAt - Date.now()),
          };
        }
        if (timer.status === "paused") {
          return {
            ...timer,
            status: "running",
            endsAt: Date.now() + timer.remainingMs,
          };
        }
        return timer;
      })
    );
    setNow(Date.now());
  }, []);

  const stop = useCallback((id) => {
    setTimers((prev) => prev.filter((timer) => timer.id !== id));
  }, []);

  const value = useMemo(
    () => ({ timers, now, startTimer, toggle, stop }),
    [timers, now, startTimer, toggle, stop]
  );

  return (
    <TimersContext.Provider value={value}>{children}</TimersContext.Provider>
  );
};

export const useTimers = () => {
  const context = useContext(TimersContext);
  if (!context) {
    throw new Error("useTimers must be used within a TimersProvider");
  }
  return context;
};

export default useTimers;
