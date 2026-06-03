import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../api/axiosInstance';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // chargement initial

  // Chargement de l'utilisateur au démarrage (si token présent)
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      api.get('/api/auth/me/')
        .then((res) => setUser(res.data))
        .catch(() => {
          localStorage.clear();
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (email, password) => {
    const res = await api.post('/api/auth/login/', { email, password });
    const { access, refresh } = res.data;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    // Récupérer le profil complet
    const meRes = await api.get('/api/auth/me/');
    setUser(meRes.data);
    return meRes.data; // retourne le profil pour la redirection
  }, []);

  const logout = useCallback(async () => {
    try {
      const refresh = localStorage.getItem('refresh_token');
      if (refresh) await api.post('/api/auth/logout/', { refresh });
    } catch { /* silencieux */ }
    localStorage.clear();
    setUser(null);
  }, []);

  const value = { user, loading, login, logout };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}
