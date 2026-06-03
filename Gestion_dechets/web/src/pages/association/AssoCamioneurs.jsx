import { useEffect, useState, useCallback } from 'react';
import api from '../../api/axiosInstance';
import { useToast } from '../../context/ToastContext';
import { unwrapList, getErrorMessage } from '../../utils/api';
import { MdCheckCircle, MdCancel } from 'react-icons/md';

export default function AssoCamioneurs() {
  const [liens, setLiens] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');
  const toast = useToast();

  const fetchLiens = useCallback(() => {
    setLoading(true);
    const params = filter ? { statut: filter } : {};
    api.get('/api/associations/camioneurs/', { params })
      .then((res) => setLiens(unwrapList(res.data)))
      .catch(() => toast('Erreur lors du chargement.', 'error'))
      .finally(() => setLoading(false));
  }, [filter, toast]);

  useEffect(() => { fetchLiens(); }, [fetchLiens]);

  const handleAction = async (camioneurId, action) => {
    try {
      await api.post(`/api/associations/camioneurs/${camioneurId}/action/`, { action });
      toast(
        action === 'accepter' ? 'Camioneur accepté dans votre réseau.' : 'Demande refusée.',
        action === 'accepter' ? 'success' : 'error',
      );
      fetchLiens();
    } catch (err) {
      toast(getErrorMessage(err, 'Action impossible.'), 'error');
    }
  };

  const pending = liens.filter((l) => l.statut === 'en_attente');
  const others = liens.filter((l) => l.statut !== 'en_attente');

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Camioneurs partenaires</h1>
          <p className="page-subtitle">
            Gérez les camioneurs liés à votre association pour les collectes
          </p>
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
          <option value="">Tous</option>
          <option value="en_attente">En attente</option>
          <option value="accepte">Acceptés</option>
          <option value="refuse">Refusés</option>
        </select>
      </div>

      {loading ? (
        <div className="spinner-container"><div className="spinner" /></div>
      ) : liens.length === 0 ? (
        <div className="empty-state card">
          <span style={{ fontSize: 48 }}>🚛</span>
          <p>Aucun camioneur lié pour le moment.</p>
          <p className="text-muted text-sm">
            Les demandes de liaison apparaîtront ici lorsqu&apos;un camioneur sollicitera votre association (app mobile).
          </p>
        </div>
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
                      <tr><th>Nom</th><th>Email</th><th>Permis</th><th>Actions</th></tr>
                    </thead>
                    <tbody>
                      {pending.map((l) => (
                        <tr key={l.id}>
                          <td><strong>{l.camioneur_nom}</strong></td>
                          <td>{l.camioneur_email}</td>
                          <td><code>{l.camioneur_permis}</code></td>
                          <td>
                            <div className="flex gap-8">
                              <button
                                type="button"
                                className="btn btn-success btn-sm"
                                onClick={() => handleAction(l.camioneur, 'accepter')}
                              >
                                <MdCheckCircle /> Accepter
                              </button>
                              <button
                                type="button"
                                className="btn btn-danger btn-sm"
                                onClick={() => handleAction(l.camioneur, 'refuser')}
                              >
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
                      <tr><th>Nom</th><th>Email</th><th>Statut</th><th>Date</th></tr>
                    </thead>
                    <tbody>
                      {others.map((l) => (
                        <tr key={l.id}>
                          <td><strong>{l.camioneur_nom}</strong></td>
                          <td>{l.camioneur_email}</td>
                          <td>
                            <span className={`badge ${l.statut === 'accepte' ? 'badge-success' : 'badge-danger'}`}>
                              {l.statut === 'accepte' ? 'Accepté' : 'Refusé'}
                            </span>
                          </td>
                          <td className="text-sm">
                            {l.date_demande
                              ? new Date(l.date_demande).toLocaleDateString('fr-FR')
                              : '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}
