import api from './client';

export async function updatePosition(latitude, longitude, disponible) {
  const payload = { latitude, longitude };
  if (disponible !== undefined) payload.disponible = disponible;
  const { data } = await api.put('/api/mobile/camioneur/position/', payload);
  return data;
}

export async function fetchProfilCamioneur() {
  const { data } = await api.get('/api/mobile/camioneur/profil/');
  return data;
}

export async function patchProfilCamioneur(payload) {
  const { data } = await api.patch('/api/mobile/camioneur/profil/', payload);
  return data;
}
