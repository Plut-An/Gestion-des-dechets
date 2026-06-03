import { useEffect, useState, useCallback } from 'react';
import api from '../../api/axiosInstance';
import { useToast } from '../../context/ToastContext';
import { unwrapList } from '../../utils/api';

export default function AssoMembres() {
  const [membres, setMembres] = useState([]);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  const fetchMembres = useCallback(() => {
    setLoading(true);
    api.get('/api/associations/membres/')
      .then((res) => setMembres(unwrapList(res.data)))
      .catch(() => toast('Erreur lors du chargement.', 'error'))
      .finally(() => setLoading(false));
  }, [toast]);

  useEffect(() => { fetchMembres(); }, [fetchMembres]);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Membres</h1>
          <p className="page-subtitle">Citoyens ayant une adhésion acceptée</p>
        </div>
        <span className="badge badge-success" style={{ fontSize: 'var(--text-sm)', padding: '8px 16px' }}>
          {membres.length} membre{membres.length !== 1 ? 's' : ''}
        </span>
      </div>

      <div className="card" style={{ padding: 0 }}>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Nom</th>
                <th>Email</th>
                <th>Éco-points</th>
                <th>Membre depuis</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={4} style={{ textAlign: 'center', padding: 40 }}>
                  <div className="spinner" style={{ margin: '0 auto' }} />
                </td></tr>
              ) : membres.length === 0 ? (
                <tr><td colSpan={4}><div className="empty-state">Aucun membre pour le moment.</div></td></tr>
              ) : membres.map((m) => (
                <tr key={m.id}>
                  <td><strong>{m.citoyen_nom}</strong></td>
                  <td>{m.citoyen_email}</td>
                  <td>{m.citoyen_eco_points ?? 0} pts</td>
                  <td className="text-sm">
                    {m.date_demande
                      ? new Date(m.date_demande).toLocaleDateString('fr-FR')
                      : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
