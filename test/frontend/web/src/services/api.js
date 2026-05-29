/**
 * Client HTTP Axios — API Django (administration).
 */
import axios from "axios";

export const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

export const TOKEN_STORAGE_KEY = "auth_token";

export function getStoredToken() {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setStoredToken(token) {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearStoredToken() {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

export function isAuthenticated() {
  return Boolean(getStoredToken());
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = getStoredToken();
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

export async function login(username, password) {
  const { data } = await api.post("/login/", { username, password });
  return data;
}

/** Scénario 1 — Liste des citoyens en attente de validation. */
export async function fetchCitoyensEnAttente() {
  const { data } = await api.get("/admin/citoyens-enattente/");
  return data;
}

/** Scénario 1 — Activation du compte citoyen par l'administrateur. */
export async function validerCitoyen(userId) {
  const { data } = await api.patch(`/admin/valider-citoyen/${userId}/`);
  return data;
}

/** Dashboard — Statistiques globales. */
export async function fetchDashboardStats() {
  const { data } = await api.get("/admin/dashboard-stats/");
  return data;
}

export default api;
