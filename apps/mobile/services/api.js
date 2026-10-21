import axios from "axios";

export const API_URL = process.env.EXPO_PUBLIC_API_URL?.trim();
export const API_KEY = process.env.EXPO_PUBLIC_APP_API_KEY?.trim();

const AUTH_HEADERS = API_KEY ? { "X-Api-Key": API_KEY } : {};

if (!API_URL) {
  console.error(
    "[api] EXPO_PUBLIC_API_URL is not set. Every request will fail. " +
      "Set it in .env / .env.production before building."
  );
}

if (!API_KEY) {
  console.error(
    "[api] EXPO_PUBLIC_APP_API_KEY is not set. Every request will 401. " +
      "It must match APP_API_KEY on the backend."
  );
}

const api = axios.create({
  baseURL: API_URL,
  timeout: 15000,
  headers: { ...AUTH_HEADERS },
});

export const buildRecipeImageUrl = (source, image, width) => {
  if (!image || !API_URL) return null;
  const base = `${API_URL}/images/${source}/${image}`;
  const uri = width ? `${base}?w=${width}` : base;
  return { uri, headers: { ...AUTH_HEADERS } };
};

const apiService = {
  getRecipes: (params) => api.get("/recipes", { params }),
  getFavorites: () => api.get("/recipes", { params: { favorites_only: true } }),
  searchRecipes: (params = {}) =>
    api.get("/recipes/search", { params }),
  getRecipe: (id, lang) =>
    api.get(`/recipes/${id}`, { params: { lang } }),
  createRecipe: (data) => api.post("/recipes/", data),
  updateRecipe: (id, data) => api.put(`/recipes/${id}`, data),
  deleteRecipe: (id) => api.delete(`/recipes/${id}`),
  uploadRecipeImage: (id, asset) => {
    const form = new FormData();
    form.append("file", {
      uri: asset.uri,
      name: asset.fileName || `recipe-${id}.jpg`,
      type: asset.mimeType || "image/jpeg",
    });

    return api.post(`/recipes/${id}/image`, form, { timeout: 30000 });
  },
  deleteRecipeImage: (id) => api.delete(`/recipes/${id}/image`),
  toggleFavorite: (id) => api.put(`/recipes/${id}/favorite`),
  scaleRecipe: (id, persons) =>
    api.get(`/recipes/${id}/scale`, { params: { persons } }),
  addTimer: (id, data) => api.post(`/recipes/${id}/timers`, data),
  deleteTimer: (id, timerId) => api.delete(`/recipes/${id}/timers/${timerId}`),
  markCooked: (id, date) =>
    api.post(`/recipes/${id}/cooked`, null, { params: { date } }),
  unmarkCooked: (id, date) => api.delete(`/recipes/${id}/cooked/${date}`),
  getHistory: () => api.get("/history"),
  chat: (message, language) => api.post("/chat", { message, language }),
  syncRecipes: () => api.post("/ingestion/sync-recipes"),
  warmup: () => api.get("/warmup"),
};

export default apiService;
export { api, apiService };