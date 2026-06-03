import { useEffect, useState, useCallback } from 'react';
import api from '../../api/axiosInstance';
import { useToast } from '../../context/ToastContext';
import { unwrapList, useDebouncedValue, getErrorMessage } from '../../utils/api';
import { MdCheckCircle, MdCancel, MdSearch, MdAdd, MdClose } from 'react-icons/md';

const STATUT_LABEL = {
  en_attente: { text: 'En attente', cls: 'badge-warning' },
  accepte: { text: 'Validé', cls: 'badge-success' },
  refuse: { text: 'Refusé', cls: 'badge-danger' },
};

export default function AdminCitoyens() {
  const [citoyens, setCitoyens] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    email: '', nom: '', password: 'ChangeMe123!', adresse: '', langue: 'FR',
  });
  const debouncedSearch = useDebouncedValue(search);
  const toast = useToast();

  const fetchCitoyens = useCallback(() => {
    setLoading(true);
    const params = {};
    if (debouncedSearch) params.search = debouncedSearch;
    if (filter) params.statut = filter;
    api.get('/api/admin/citoyens/', { params })
      .then((res) => setCitoyens(unwrapList(res.data)))
      .catch(() => toast('Erreur lors du chargement.', 'error'))
      .finally(() => setLoading(false));
  }, [debouncedSearch, filter, toast]);

  useEffect(() => { fetchCitoyens(); }, [fetchCitoyens]);

  const handleAction = async (id, action) => {
    try {
      await api.post(`/api/admin/citoyens/${id}/valider/`, { action });
      toast(action === 'accepter' ? 'Compte validé !' : 'Compte refusé.', action === 'accepter' ? 'success' : 'error');
      fetchCitoyens();
    } catch (err) {
      toast(getErrorMessage(err, 'Action impossible.'), 'error');
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.post('/api/admin/citoyens/', { ...form, role: 'citoyen' });
      toast('Citoyen créé avec succès.', 'success');
      setShowModal(false);
      setForm({ email: '', nom: '', password: 'ChangeMe123!', adresse: '', langue: 'FR' });
      fetchCitoyens();
    } catch (err) {
      toast(getErrorMessage(err), 'error');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Gestion des Citoyens</h1>
          <p className="page-subtitle">Validation et supervision des comptes citoyens</p>
        </div>
        <button type="button" className="btn btn-primary" onClick={() => setShowModal(true)}>
          <MdAdd /> Nouveau citoyen
        </button>
      </div>

      <div className="filters-bar">
        <div className="search-box">
          <MdSearch className="search-icon" />
          <input
            className="form-input search-input"
            placeholder="Rechercher par nom ou email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select
          className="form-input filter-select"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="">Tous les statuts</option>
          <option value="en_attente">En attente</option>
          <option value="accepte">Validés</option>
          <option value="refuse">Refusés</option>
        </select>
      </div>

      <div className="card" style={{ padding: 0 }}>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Nom</th>
                <th>Email</th>
                <th>Adresse</th>
                <th>Éco-points</th>
                <th>Statut</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={6} style={{ textAlign: 'center', padding: 40 }}>
                  <div className="spinner" style={{ margin: '0 auto' }} />
                </td></tr>
              ) : citoyens.length === 0 ? (
                <tr><td colSpan={6}><div className="empty-state">Aucun citoyen trouvé.</div></td></tr>
              ) : citoyens.map((c) => {
                const s = STATUT_LABEL[c.statut_inscription] || { text: c.statut_inscription, cls: 'badge-neutral' };
                return (
                  <tr key={c.id}>
                    <td><strong>{c.nom}</strong></td>
                    <td>{c.email}</td>
                    <td>{c.adresse || '—'}</td>
                    <td>{c.solde_eco_points ?? 0} pts</td>
                    <td><span className={`badge ${s.cls}`}>{s.text}</span></td>
                    <td>
                      {c.statut_inscription === 'en_attente' ? (
                        <div className="flex gap-8">
                          <button type="button" className="btn btn-success btn-sm" onClick={() => handleAction(c.id, 'accepter')}>
                            <MdCheckCircle /> Valider
                          </button>
                          <button type="button" className="btn btn-danger btn-sm" onClick={() => handleAction(c.id, 'refuser')}>
                            <MdCancel /> Refuser
                          </button>
                        </div>
                      ) : (
                        <span className="text-muted text-sm">—</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Créer un citoyen</h2>
              <button type="button" className="modal-close" onClick={() => setShowModal(false)}><MdClose /></button>
            </div>
            <form className="modal-form" onSubmit={handleCreate}>
              <div className="form-group">
                <label className="form-label">Nom *</label>
                <input className="form-input" value={form.nom} onChange={(e) => setForm({ ...form, nom: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Email *</label>
                <input type="email" className="form-input" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Mot de passe *</label>
                <input type="password" className="form-input" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Adresse</label>
                <input className="form-input" value={form.adresse} onChange={(e) => setForm({ ...form, adresse: e.target.value })} />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-ghost" onClick={() => setShowModal(false)}>Annuler</button>
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
