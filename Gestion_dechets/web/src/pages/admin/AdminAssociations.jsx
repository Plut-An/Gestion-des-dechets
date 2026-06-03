import { useEffect, useState, useCallback } from 'react';
import api from '../../api/axiosInstance';
import { useToast } from '../../context/ToastContext';
import { unwrapList, getErrorMessage } from '../../utils/api';
import { MdAdd, MdClose, MdDelete } from 'react-icons/md';

export default function AdminAssociations() {
  const [assos, setAssos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({
    nom: '', ville: '', description: '', email: '', password: '',
  });
  const [saving, setSaving] = useState(false);
  const toast = useToast();

  const fetchAssos = useCallback(() => {
    setLoading(true);
    api.get('/api/admin/associations/')
      .then((res) => setAssos(unwrapList(res.data)))
      .catch(() => toast('Erreur lors du chargement.', 'error'))
      .finally(() => setLoading(false));
  }, [toast]);

  useEffect(() => { fetchAssos(); }, [fetchAssos]);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!form.nom || !form.ville || !form.email || !form.password) {
      toast('Nom, ville, email et mot de passe requis.', 'warning');
      return;
    }
    setSaving(true);
    try {
      await api.post('/api/admin/associations/', form);
      toast('Association créée avec succès !', 'success');
      setShowModal(false);
      setForm({ nom: '', ville: '', description: '', email: '', password: '' });
      fetchAssos();
    } catch (err) {
      toast(getErrorMessage(err), 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id, nom) => {
    if (!window.confirm(`Supprimer l'association « ${nom} » ? Cette action est irréversible.`)) return;
    try {
      await api.delete(`/api/admin/associations/${id}/`);
      toast('Association supprimée.', 'success');
      fetchAssos();
    } catch (err) {
      toast(getErrorMessage(err, 'Suppression impossible.'), 'error');
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Associations</h1>
          <p className="page-subtitle">Gestion des associations écologiques</p>
        </div>
        <button type="button" className="btn btn-primary" onClick={() => setShowModal(true)}>
          <MdAdd /> Nouvelle association
        </button>
      </div>

      <div className="card" style={{ padding: 0 }}>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Nom</th>
                <th>Compte</th>
                <th>Ville</th>
                <th>Membres</th>
                <th>Camioneurs</th>
                <th>Description</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: 40 }}>
                    <div className="spinner" style={{ margin: '0 auto' }} />
                  </td>
                </tr>
              ) : assos.length === 0 ? (
                <tr>
                  <td colSpan={7}>
                    <div className="empty-state">Aucune association enregistrée.</div>
                  </td>
                </tr>
              ) : (
                assos.map((a) => (
                  <tr key={a.id}>
                    <td><strong>{a.nom}</strong></td>
                    <td className="text-sm">{a.email || '—'}</td>
                    <td>{a.ville || '—'}</td>
                    <td>{a.nb_membres ?? 0}</td>
                    <td>{a.nb_camioneurs ?? 0}</td>
                    <td className="text-muted text-sm">{a.description || '—'}</td>
                    <td>
                      <button
                        type="button"
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(a.id, a.nom)}
                        title="Supprimer"
                      >
                        <MdDelete />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Nouvelle association</h2>
              <button type="button" className="modal-close" onClick={() => setShowModal(false)}>
                <MdClose />
              </button>
            </div>
            <form className="modal-form" onSubmit={handleCreate}>
              <div className="form-group">
                <label className="form-label">Nom de l&apos;association *</label>
                <input
                  className="form-input"
                  placeholder="Ex: Asso Ecolo Mada"
                  value={form.nom}
                  onChange={(e) => setForm({ ...form, nom: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Email de connexion *</label>
                <input
                  type="email"
                  className="form-input"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Mot de passe *</label>
                <input
                  type="password"
                  className="form-input"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Ville *</label>
                <input
                  className="form-input"
                  value={form.ville}
                  onChange={(e) => setForm({ ...form, ville: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea
                  className="form-input"
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-ghost" onClick={() => setShowModal(false)}>
                  Annuler
                </button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? 'Création...' : 'Créer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
