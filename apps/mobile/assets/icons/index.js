// Timer and oven icon registry.
// Metro requires static require() calls, so add one line per new PNG here.
export const TIMER_ICONS = {
  bacon: require("./bacon.png"),
  beans: require("./beans.png"),
  broccoli: require("./broccoli.png"),
  cauliflower: require("./cauliflower.png"),
  cheese: require("./cheese.png"),
  cooking: require("./cooking.png"),
  frying: require("./frying.png"),
  garlic: require("./garlic.png"),
  gnocci: require("./gnocci.png"),
  leek: require("./leek.png"),
  macaroni: require("./macaroni.png"),
  meat: require("./meat.png"),
  noodles: require("./noodles.png"),
  oil: require("./oil.png"),
  onion: require("./onion.png"),
  oven: require("./oven.png"),
  paprika: require("./paprika.png"),
  pasta: require("./pasta.png"),
  pot: require("./pot.png"),
  rice: require("./rice.png"),
  sauce: require("./sauce.png"),
  spices: require("./spices.png"),
  tomato: require("./tomato.png"),
  vegetables: require("./vegetables.png"),
};

export const TIMER_ICON_KEYS = Object.keys(TIMER_ICONS);

export const getTimerIcon = (key) => (key ? TIMER_ICONS[key] : null);

export const OVEN_MODE_ICONS = {
  default: require("./toaster-oven.png"),
  fan: require("./hetelucht.png"),
  conventional: require("./boven-onder.png"),
};

export const OVEN_MODES = [
  { value: null, label: "Oven" },
  { value: "fan", label: "Hetelucht" },
  { value: "conventional", label: "Boven-onder" },
];

export const getOvenModeIcon = (mode) =>
  OVEN_MODE_ICONS[mode] || OVEN_MODE_ICONS.default;

export default TIMER_ICONS;
