import { useEffect, useState, useCallback } from 'react';
import api from '../../api/axiosInstance';
import { useToast } from '../../context/ToastContext';
import { unwrapList, getErrorMessage } from '../../utils/api';
import { MdAdd, MdClose, MdDelete } from 'react-icons/md';

export default function AssoAnnonces() {
  const [annonces, setAnnonces]   = useState([]);
  const [loading, setLoading]     = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [saving, setSaving]       = useState(false);
  const [form, setForm]           = useState({ titre: '', contenu: '' });
  const toast = useToast();

  const fetchAnnonces = useCallback(() => {
    setLoading(true);
    api.get(`/api/mobile/association/annonces/`)
      .then((res) => setAnnonces(unwrapList(res.data)))
      .catch(() => toast('Erreur lors du chargement.', 'error'))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { fetchAnnonces(); }, [fetchAnnonces]);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!form.titre || !form.contenu) {
      toast('Titre et contenu requis.', 'warning'); return;
    }
    setSaving(true);
    try {
      await api.post(`/api/mobile/association/annonces/`, form);
      toast('Annonce publiée !', 'success');
      setShowModal(false);
      setForm({ titre: '', contenu: '' });
      fetchAnnonces();
    } catch (err) {
      toast(getErrorMessage(err, 'Erreur lors de la publication.'), 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Supprimer cette annonce ?')) return;
    try {
      await api.delete(`/api/mobile/association/annonces/${id}/`);
      toast('Annonce supprimée.', 'success');
      fetchAnnonces();
    } catch {
      toast('Suppression impossible.', 'error');
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Annonces</h1>
          <p className="page-subtitle">Publiez des informations pour vos membres</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          <MdAdd /> Nouvelle annonce
        </button>
      </div>

      {loading ? (
        <div className="spinner-container"><div className="spinner" /></div>
      ) : annonces.length === 0 ? (
        <div className="empty-state card">
          <span style={{ fontSize: 48 }}>📢</span>
          <p>Aucune annonce publiée. Créez votre première annonce !</p>
        </div>
      ) : (
        <div className="annonces-list">
          {annonces.map((a) => (
            <div key={a.id} className="card annonce-card">
              <div className="annonce-header">
                <div>
                  <h3 className="annonce-title">{a.titre}</h3>
                  <p className="annonce-date">
                    Publié le {new Date(a.date_publication).toLocaleDateString('fr-FR', {
                      day: '2-digit', month: 'long', year: 'numeric'
                    })}
                  </p>
                </div>
                <button
                  className="btn btn-danger btn-sm"
                  onClick={() => handleDelete(a.id)}
                  title="Supprimer"
                >
                  <MdDelete />
                </button>
              </div>
              <p className="annonce-contenu">{a.contenu}</p>
            </div>
          ))}
        </div>
      )}

      {/* Modal de création */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Nouvelle annonce</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}><MdClose /></button>
            </div>
            <form className="modal-form" onSubmit={handleCreate}>
              <div className="form-group">
                <label className="form-label">Titre *</label>
                <input
                  className="form-input"
                  placeholder="Ex: Rappel — Événement ce samedi"
                  value={form.titre}
                  onChange={(e) => setForm({ ...form, titre: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Contenu *</label>
                <textarea
                  className="form-input"
                  placeholder="Rédigez votre annonce ici..."
                  rows={5}
                  value={form.contenu}
                  onChange={(e) => setForm({ ...form, contenu: e.target.value })}
                />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-ghost" onClick={() => setShowModal(false)}>
                  Annuler
                </button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? 'Publication...' : 'Publier'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
