import api from './client';

export async function listEvenements() {
  const { data } = await api.get('/api/mobile/evenements/');
  return data;
}

export async function participerEvenement(evId) {
  const { data } = await api.post(`/api/mobile/evenements/${evId}/participer/`);
  return data;
}

export async function annulerParticipation(evId) {
  const { data } = await api.delete(`/api/mobile/evenements/${evId}/participer/`);
  return data;
}

export async function listMesParticipations() {
  const { data } = await api.get('/api/mobile/evenements/mes-participations/');
  return data;
}

export async function listAnnonces() {
  const { data } = await api.get('/api/mobile/annonces/');
  return data;
}

export async function listCommentaires(evId) {
  const { data } = await api.get(`/api/mobile/evenements/${evId}/commentaires/`);
  return data;
}

export async function addCommentaire(evId, contenu) {
  const { data } = await api.post(`/api/mobile/evenements/${evId}/commentaires/`, {
    contenu,
  });
  return data;
}
