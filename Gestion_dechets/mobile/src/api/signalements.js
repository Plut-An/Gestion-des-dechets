import api from './client';

export async function listSignalements() {
  const { data } = await api.get('/api/mobile/signalements/');
  return data;
}

export async function createSignalement(formData) {
  const { data } = await api.post('/api/mobile/signalements/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function getSignalement(id) {
  const { data } = await api.get(`/api/mobile/signalements/${id}/`);
  return data;
}

export async function listSignalementsProches(lat, lng, rayon = 50) {
  const { data } = await api.get('/api/mobile/camioneur/signalements/', {
    params: { lat, lng, rayon },
  });
  return data;
}

export async function accepterSignalement(id) {
  const { data } = await api.post(`/api/mobile/camioneur/signalements/${id}/accepter/`);
  return data;
}

export async function validerSignalement(id) {
  const { data } = await api.post(`/api/mobile/camioneur/signalements/${id}/valider/`);
  return data;
}

export async function refuserSignalement(id) {
  const { data } = await api.post(`/api/mobile/camioneur/signalements/${id}/refuser/`);
  return data;
}

export async function listMesCollectes() {
  const { data } = await api.get('/api/mobile/camioneur/collectes/');
  return data;
}
