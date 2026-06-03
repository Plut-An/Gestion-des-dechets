import { useEffect, useState, useCallback } from 'react';
import api from '../../api/axiosInstance';
import { useToast } from '../../context/ToastContext';
import { unwrapList, getErrorMessage } from '../../utils/api';
import { MdCheckCircle, MdCancel } from 'react-icons/md';

export default function AssoAdhesions() {
  const [adhesions, setAdhesions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');
  const toast = useToast();

  const fetchAdhesions = useCallback(() => {
    setLoading(true);
    const params = filter ? { statut: filter } : {};
    api.get('/api/associations/adhesions/', { params })
      .then((res) => setAdhesions(unwrapList(res.data)))
      .catch(() => toast('Erreur lors du chargement.', 'error'))
      .finally(() => setLoading(false));
  }, [filter, toast]);

  useEffect(() => { fetchAdhesions(); }, [fetchAdhesions]);

  const handleAction = async (adhesionId, action) => {
    try {
      await api.post(`/api/associations/adhesions/${adhesionId}/action/`, { action });
      toast(action === 'accepter' ? 'Membre accepté !' : 'Demande refusée.', action === 'accepter' ? 'success' : 'error');
      fetchAdhesions();
    } catch (err) {
      toast(getErrorMessage(err, 'Action impossible.'), 'error');
    }
  };

  const pending = adhesions.filter((a) => a.statut === 'en_attente');
  const others = adhesions.filter((a) => a.statut !== 'en_attente');

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Demandes d&apos;adhésion</h1>
          <p className="page-subtitle">Gérez les demandes d&apos;adhésion à votre association</p>
        </div>
        <span className="badge badge-warning" style={{ fontSize: 'var(--text-sm)', padding: '8px 16px' }}>
          {pending.length} en attente
        </span>
      </div>

      <div className="filters-bar">
        <select
          className="form-input filter-select"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="">Toutes</option>
          <option value="en_attente">En attente</option>
          <option value="accepte">Acceptées</option>
          <option value="refuse">Refusées</option>
        </select>
      </div>

      {loading ? (
        <div className="spinner-container"><div className="spinner" /></div>
      ) : (
        <>
          {pending.length > 0 && (
            <>
              <h2 style={{ fontSize: 'var(--text-base)', fontWeight: 700, marginBottom: 12, color: 'var(--text-secondary)' }}>
                En attente de décision
              </h2>
              <div className="card" style={{ padding: 0, marginBottom: 24 }}>
                <div className="table-wrapper">
                  <table className="data-table">
                    <thead>
                      <tr><th>Citoyen</th><th>Email</th><th>Éco-points</th><th>Date</th><th>Actions</th></tr>
                    </thead>
                    <tbody>
                      {pending.map((a) => (
                        <tr key={a.id}>
                          <td><strong>{a.citoyen_nom || '—'}</strong></td>
                          <td>{a.citoyen_email || '—'}</td>
                          <td>{a.citoyen_eco_points ?? 0} pts</td>
                          <td>{new Date(a.date_demande).toLocaleDateString('fr-FR')}</td>
                          <td>
                            <div className="flex gap-8">
                              <button type="button" className="btn btn-success btn-sm" onClick={() => handleAction(a.id, 'accepter')}>
                                <MdCheckCircle /> Accepter
                              </button>
                              <button type="button" className="btn btn-danger btn-sm" onClick={() => handleAction(a.id, 'refuser')}>
                                <MdCancel /> Refuser
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}

          {others.length > 0 && (
            <>
              <h2 style={{ fontSize: 'var(--text-base)', fontWeight: 700, marginBottom: 12, color: 'var(--text-secondary)' }}>
                Historique
              </h2>
              <div className="card" style={{ padding: 0 }}>
                <div className="table-wrapper">
                  <table className="data-table">
                    <thead>
                      <tr><th>Citoyen</th><th>Email</th><th>Statut</th><th>Motif refus</th></tr>
                    </thead>
                    <tbody>
                      {others.map((a) => (
                        <tr key={a.id}>
                          <td><strong>{a.citoyen_nom || '—'}</strong></td>
                          <td>{a.citoyen_email || '—'}</td>
                          <td>
                            <span className={`badge ${a.statut === 'accepte' ? 'badge-success' : 'badge-danger'}`}>
                              {a.statut === 'accepte' ? 'Accepté' : 'Refusé'}
                            </span>
                          </td>
                          <td className="text-muted text-sm">{a.motif_refus || '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}

          {adhesions.length === 0 && (
            <div className="empty-state card">
              <span style={{ fontSize: 48 }}>📭</span>
              <p>Aucune demande d&apos;adhésion pour le moment.</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
