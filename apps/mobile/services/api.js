import axios from "axios";

export const API_URL = process.env.EXPO_PUBLIC_API_URL?.trim();

const api = axios.create({
  baseURL: API_URL,
});

export const buildRecipeImageUrl = (source, image) => {
  if (!image || !API_URL) return null;
  return `${API_URL}/images/${source}/${image}`;
};

const apiService = {
  getRecipes: (params) => api.get("/recipes", { params }),
  getFavorites: () => api.get("/recipes", { params: { favorites_only: true } }),
  searchRecipes: (query) =>
    api.get("/recipes/search", { params: { q: query } }),
  getRecipe: (id, lang) =>
    api.get(`/recipes/${id}`, { params: { lang } }),
  createRecipe: (data) => api.post("/recipes/", data),
  updateRecipe: (id, data) => api.put(`/recipes/${id}`, data),
  deleteRecipe: (id) => api.delete(`/recipes/${id}`),
  toggleFavorite: (id) => api.put(`/recipes/${id}/favorite`),
  scaleRecipe: (id, persons) =>
    api.get(`/recipes/${id}/scale`, { params: { persons } }),
  addTimer: (id, data) => api.post(`/recipes/${id}/timers`, data),
  deleteTimer: (id, timerId) => api.delete(`/recipes/${id}/timers/${timerId}`),
  chat: (message, language) => api.post("/chat", { message, language }),
  syncRecipes: () => api.post("/ingestion/sync-recipes"),
  warmup: () => api.get("/warmup"),
};

export default apiService;
export { api, apiService };
