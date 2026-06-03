import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as authApi from '../api/auth';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    const token = await AsyncStorage.getItem('access_token');
    if (!token) {
      setUser(null);
      return;
    }
    const me = await authApi.fetchMe();
    setUser(me);
  }, []);

  useEffect(() => {
    (async () => {
      try {
        await loadUser();
      } catch {
        await AsyncStorage.multiRemove(['access_token', 'refresh_token']);
        setUser(null);
      } finally {
        setLoading(false);
      }
    })();
  }, [loadUser]);

  const persistTokens = async (access, refresh) => {
    await AsyncStorage.setItem('access_token', access);
    if (refresh) await AsyncStorage.setItem('refresh_token', refresh);
  };

  const login = async (email, password) => {
    const data = await authApi.login(email, password);
    await persistTokens(data.access, data.refresh);
    const me = await authApi.fetchMe();
    setUser(me);
    return me;
  };

  const register = async (role, payload) => {
    const data =
      role === 'citoyen'
        ? await authApi.registerCitoyen(payload)
        : await authApi.registerCamioneur(payload);

    if (!data?.access) {
      throw new Error('Réponse serveur invalide (token manquant).');
    }

    await persistTokens(data.access, data.refresh);

    try {
      const me = await authApi.fetchMe();
      setUser(me);
      return me;
    } catch {
      // Inscription OK mais /me/ inaccessible — profil minimal depuis la réponse
      const minimal = {
        id: data.user?.id,
        nom: data.user?.nom,
        email: data.user?.email,
        role: data.user?.role,
      };
      setUser(minimal);
      return minimal;
    }
  };

  const logout = async () => {
    const refresh = await AsyncStorage.getItem('refresh_token');
    try {
      await authApi.logout(refresh);
    } catch {
      /* ignore */
    }
    await AsyncStorage.multiRemove(['access_token', 'refresh_token']);
    setUser(null);
  };

  const refreshProfile = async () => {
    const me = await authApi.fetchMe();
    setUser(me);
    return me;
  };

  return (
    <AuthContext.Provider
      value={{ user, loading, login, register, logout, refreshProfile }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
