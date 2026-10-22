export const TIMER_COLORS = [
  {
    value: "#e74c3c",
    label: "Rood",
    background: "#fdecea",
    border: "#f5c6c2",
    text: "#be123c",
  },
  {
    value: "#f39c12",
    label: "Oranje",
    background: "#fef3c7",
    border: "#fcd34d",
    text: "#b45309",
  },
  {
    value: "#16a34a",
    label: "Groen",
    background: "#dcfce7",
    border: "#86efac",
    text: "#15803d",
  },
  {
    value: "#0088fa",
    label: "Blauw",
    background: "#e0f2fe",
    border: "#7dd3fc",
    text: "#0369a1",
  },
  {
    value: "#8e44ad",
    label: "Paars",
    background: "#f3e8ff",
    border: "#d8b4fe",
    text: "#7e22ce",
  },
];

export const DEFAULT_TIMER_COLOR = TIMER_COLORS[0].value;

export const PAUSED_TIMER_COLOR = "#6b7280";

export const getTimerColor = (value) =>
  TIMER_COLORS.find((color) => color.value === value) || TIMER_COLORS[0];

export default TIMER_COLORS;
