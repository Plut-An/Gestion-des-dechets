import api from './client';

export async function login(email, password) {
  const { data } = await api.post('/api/auth/login/', { email, password });
  return data;
}

export async function registerCitoyen({ nom, email, password, password2, adresse = '' }) {
  const { data } = await api.post('/api/auth/register/citoyen/', {
    nom: nom.trim(),
    email: email.trim().toLowerCase(),
    password,
    password2,
    adresse: adresse.trim(),
    langue: 'FR',
  });
  return data;
}

export async function registerCamioneur({ nom, email, password, password2, numero_permis }) {
  const { data } = await api.post('/api/auth/register/camioneur/', {
    nom: nom.trim(),
    email: email.trim().toLowerCase(),
    password,
    password2,
    numero_permis: numero_permis.trim(),
    langue: 'FR',
  });
  return data;
}

export async function fetchMe() {
  const { data } = await api.get('/api/auth/me/');
  return data;
}

export async function changePassword(payload) {
  const { data } = await api.post('/api/auth/change-password/', payload);
  return data;
}

export async function logout(refresh) {
  if (refresh) {
    await api.post('/api/auth/logout/', { refresh });
  }
}
