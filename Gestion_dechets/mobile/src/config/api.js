import { Platform } from 'react-native';
import Constants from 'expo-constants';

function normalizeApiUrl(url) {
  let u = (url || '').trim();
  if (!u) return '';
  u = u.replace(/^http\/\//i, 'http://').replace(/^https\/\//i, 'https://');
  if (!/^https?:\/\//i.test(u)) {
    u = `http://${u}`;
  }
  return u.replace(/\/$/, '');
}

/**
 * Ordre de priorité :
 * 1. EXPO_PUBLIC_API_URL (.env)
 * 2. app.config.js → extra.apiUrl
 * 3. Émulateur/simulateur uniquement
 * 4. IP LAN par défaut (téléphone physique)
 */
function resolveApiUrl() {
  const fromEnv = process.env.EXPO_PUBLIC_API_URL;
  const fromExtra = Constants.expoConfig?.extra?.apiUrl;

  const candidate = normalizeApiUrl(fromEnv || fromExtra || '');
  if (candidate) return candidate;

  // Sans config : émulateur ≠ téléphone réel
  if (!Constants.isDevice) {
    return getEmulatorUrl();
  }

  // Téléphone réel — ne jamais utiliser 10.0.2.2 ni 127.0.0.1
  return 'http://192.168.88.102:8000';
}

export const API_BASE_URL = resolveApiUrl();

if (__DEV__) {
  console.log('[ÉcoGestion] API_BASE_URL =', API_BASE_URL);
}
