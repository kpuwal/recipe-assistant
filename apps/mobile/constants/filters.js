import { CATEGORIES } from "./categories";

const categoryFilter = (value) => {
  const category = CATEGORIES.find((item) => item.value === value);

  return {
    id: value,
    emoji: category.emoji,
    label: category.label,
    params: { category: value },
  };
};

export const FILTERS = [
  { id: "all", emoji: "📚", label: "Alles", params: {} },
  {
    id: "favorites",
    emoji: "❤️",
    label: "Favs",
    params: { favorites_only: true },
  },
  { id: "quick", emoji: "⚡", label: "15 min", params: { max_time: 15 } },
  {
    id: "medium",
    emoji: "⏱",
    label: "15-25 min",
    params: { min_time: 15, max_time: 25 },
  },
  categoryFilter("pasta"),
  categoryFilter("rice"),
  categoryFilter("noodle"),
];
