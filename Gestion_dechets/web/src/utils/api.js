import { useState, useEffect } from 'react';

/** Extrait une liste depuis une réponse DRF (paginée ou tableau brut). */
export function unwrapList(data) {
  if (Array.isArray(data)) return data;
  if (data?.results && Array.isArray(data.results)) return data.results;
  return [];
}

/** Message d'erreur lisible depuis une réponse axios. */
export function getErrorMessage(err, fallback = 'Une erreur est survenue.') {
  const data = err?.response?.data;
  if (!data) return fallback;
  if (typeof data === 'string') return data;
  if (data.detail) return String(data.detail);
  const parts = [];
  Object.entries(data).forEach(([key, value]) => {
    if (Array.isArray(value)) parts.push(`${key}: ${value.join(' ')}`);
    else if (value != null) parts.push(`${key}: ${value}`);
  });
  return parts.length ? parts.join(' · ') : fallback;
}

/** datetime-local → ISO 8601 pour l'API Django. */
export function toApiDateTime(localValue) {
  if (!localValue) return '';
  const d = new Date(localValue);
  if (Number.isNaN(d.getTime())) return localValue;
  return d.toISOString();
}

/** Valeur debouncée (recherche, filtres). */
export function useDebouncedValue(value, delay = 400) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}
