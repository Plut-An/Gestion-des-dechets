import api from './client';

export async function listAssociations() {
  const { data } = await api.get('/api/associations/');
  return data;
}

export async function rejoindreAssociation(id) {
  const { data } = await api.post(`/api/associations/${id}/rejoindre/`, {
    association: id,
  });
  return data;
}
