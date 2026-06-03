export function unwrapList(data) {
  if (Array.isArray(data)) return data;
  if (data?.results) return data.results;
  return [];
}

import { API_BASE_URL } from '../config/api';

export function getErrorMessage(err, fallback = 'Une erreur est survenue.') {
  // Pas de réponse HTTP = réseau, URL incorrecte, ou serveur arrêté
  if (!err?.response) {
    if (err?.code === 'ECONNABORTED') {
      return 'Délai dépassé. Vérifiez votre connexion internet.';
    }
    if (
      err?.message === 'Network Error' ||
      err?.code === 'ERR_NETWORK' ||
      err?.message?.includes('Network request failed')
    ) {
      return (
        `Impossible de contacter le serveur.\n\n` +
        `URL actuelle : ${API_BASE_URL}\n\n` +
        `• Backend : python manage.py runserver 0.0.0.0:8000\n` +
        `• Téléphone réel : créez mobile/.env avec l'IP de votre PC\n` +
        `  EXPO_PUBLIC_API_URL=http://192.168.x.x:8000\n` +
        `• Émulateur Android : http://10.0.2.2:8000\n` +
        `Puis relancez : npx expo start -c`
      );
    }
    return err?.message || fallback;
  }

  const data = err.response.data;
  if (typeof data === 'string') return data;
  if (data.detail) return String(data.detail);
  const parts = [];
  Object.entries(data).forEach(([k, v]) => {
    if (Array.isArray(v)) parts.push(`${k}: ${v.join(' ')}`);
    else if (v != null) parts.push(`${k}: ${v}`);
  });
  return parts.length ? parts.join('\n') : fallback;
}

export const TYPE_DECHET = [
  { value: 'organique', label: 'Organique' },
  { value: 'plastique', label: 'Plastique' },
  { value: 'verre', label: 'Verre' },
  { value: 'metal', label: 'Métal' },
  { value: 'mixte', label: 'Mixte' },
  { value: 'autre', label: 'Autre' },
];

export const STATUT_INSCRIPTION_LABEL = {
  en_attente: 'En attente de validation admin',
  accepte: 'Compte validé',
  refuse: 'Compte refusé',
};

export const STATUT_SIGNALEMENT = {
  signale: 'Ouvert',
  assigne: 'Assigné',
  en_cours: 'En cours',
  traite: 'Traité',
  refuse: 'Refusé',
};
