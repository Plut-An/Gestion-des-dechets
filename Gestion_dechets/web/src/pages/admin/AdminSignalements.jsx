import { useEffect, useState, useCallback } from 'react';
import api from '../../api/axiosInstance';
import { useToast } from '../../context/ToastContext';
import { unwrapList } from '../../utils/api';

const STATUT_LABEL = {
  signale: { text: 'Ouvert', cls: 'badge-warning' },
  assigne: { text: 'Assigné', cls: 'badge-accent' },
  en_cours: { text: 'En cours', cls: 'badge-accent' },
  traite: { text: 'Traité', cls: 'badge-success' },
  refuse: { text: 'Refusé', cls: 'badge-danger' },
};

export default function AdminSignalements() {
  const [signalements, setSignalements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');
  const toast = useToast();

  const fetchSignalements = useCallback(() => {
    setLoading(true);
    const params = filter ? { statut: filter } : {};
    api.get('/api/mobile/admin-signalements/', { params })
      .then((res) => setSignalements(unwrapList(res.data)))
      .catch(() => toast('Erreur lors du chargement.', 'error'))
      .finally(() => setLoading(false));
  }, [filter, toast]);

  useEffect(() => { fetchSignalements(); }, [fetchSignalements]);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Signalements</h1>
          <p className="page-subtitle">Supervision de tous les signalements citoyens</p>
        </div>
      </div>

      <div className="filters-bar">
        <select
          className="form-input filter-select"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="">Tous les statuts</option>
          <option value="signale">Ouverts</option>
          <option value="assigne">Assignés</option>
          <option value="en_cours">En cours</option>
          <option value="traite">Traités</option>
          <option value="refuse">Refusés</option>
        </select>
      </div>

      <div className="card" style={{ padding: 0 }}>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Type</th>
                <th>Citoyen</th>
                <th>Camioneur</th>
                <th>Coordonnées</th>
                <th>Statut</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={7} style={{ textAlign: 'center', padding: 40 }}>
                  <div className="spinner" style={{ margin: '0 auto' }} />
                </td></tr>
              ) : signalements.length === 0 ? (
                <tr><td colSpan={7}><div className="empty-state">Aucun signalement.</div></td></tr>
              ) : signalements.map((s) => {
                const st = STATUT_LABEL[s.statut] || { text: s.statut, cls: 'badge-neutral' };
                return (
                  <tr key={s.id}>
                    <td>{s.id}</td>
                    <td>{s.type_dechet || '—'}</td>
                    <td>{s.citoyen_nom || '—'}</td>
                    <td>{s.camioneur_nom || '—'}</td>
                    <td className="text-sm text-muted">
                      {s.latitude}, {s.longitude}
                    </td>
                    <td><span className={`badge ${st.cls}`}>{st.text}</span></td>
                    <td className="text-sm">
                      {s.date_signalement
                        ? new Date(s.date_signalement).toLocaleString('fr-FR')
                        : '—'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
