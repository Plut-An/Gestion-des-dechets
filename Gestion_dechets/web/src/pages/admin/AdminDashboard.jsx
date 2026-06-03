import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/axiosInstance';
import { useToast } from '../../context/ToastContext';
import { unwrapList } from '../../utils/api';
import {
  MdPeople, MdLocalShipping, MdApartment,
  MdWarning, MdCheckCircle, MdBarChart, MdMap
} from 'react-icons/md';
import './AdminDashboard.css';

function KpiCard({ icon, label, value, color, sublabel }) {
  return (
    <div className="kpi-card" style={{ '--kpi-color': color }}>
      <div className="kpi-icon">{icon}</div>
      <div className="kpi-body">
        <p className="kpi-value">{value ?? <span className="kpi-skeleton" />}</p>
        <p className="kpi-label">{label}</p>
        {sublabel && <p className="kpi-sublabel">{sublabel}</p>}
      </div>
    </div>
  );
}

const SIG_STATUT = {
  signale: { label: 'Ouvert', cls: 'badge-warning' },
  assigne: { label: 'Assigné', cls: 'badge-accent' },
  en_cours: { label: 'En cours', cls: 'badge-accent' },
  traite: { label: 'Traité', cls: 'badge-success' },
  refuse: { label: 'Refusé', cls: 'badge-danger' },
};

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [recentSignalements, setRecentSignalements] = useState([]);
  const toast = useToast();

  useEffect(() => {
    Promise.all([
      api.get('/api/admin/dashboard/'),
      api.get('/api/mobile/admin-signalements/', { params: { statut: 'signale' } }),
    ])
      .then(([dashRes, sigRes]) => {
        setStats(dashRes.data);
        const list = unwrapList(sigRes.data).slice(0, 5);
        setRecentSignalements(list);
      })
      .catch(() => toast('Impossible de charger les statistiques.', 'error'));
  }, [toast]);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Tableau de bord</h1>
          <p className="page-subtitle">Vue d&apos;ensemble de la plateforme ÉcoGestion</p>
        </div>
      </div>

      <div className="kpi-grid">
        <KpiCard
          icon={<MdPeople />}
          label="Citoyens inscrits"
          value={stats?.total_citoyens}
          color="hsl(195, 80%, 50%)"
          sublabel={`${stats?.citoyens_acceptes ?? '—'} validés · ${stats?.citoyens_en_attente ?? 0} en attente`}
        />
        <KpiCard
          icon={<MdLocalShipping />}
          label="Camioneurs"
          value={stats?.total_camioneurs}
          color="hsl(152, 68%, 39%)"
          sublabel={`${stats?.camioneurs_acceptes ?? '—'} validés · ${stats?.camioneurs_disponibles ?? 0} dispo.`}
        />
        <KpiCard
          icon={<MdApartment />}
          label="Associations"
          value={stats?.total_associations}
          color="hsl(271, 60%, 60%)"
        />
        <KpiCard
          icon={<MdWarning />}
          label="Signalements ouverts"
          value={stats?.signalements_en_attente}
          color="hsl(38, 92%, 55%)"
          sublabel={`${stats?.signalements_en_cours ?? 0} en collecte`}
        />
        <KpiCard
          icon={<MdCheckCircle />}
          label="Signalements traités"
          value={stats?.signalements_traites}
          color="hsl(152, 68%, 39%)"
          sublabel={`${stats?.total_signalements ?? 0} au total`}
        />
        <KpiCard
          icon={<MdBarChart />}
          label="Éco-points distribués"
          value={stats?.total_eco_points}
          color="hsl(195, 80%, 50%)"
        />
      </div>

      <div className="dashboard-grid">
        <div className="card">
          <h2 className="card-title">Comptes en attente de validation</h2>
          <div className="pending-list">
            {stats ? (
              <>
                <div className="pending-item">
                  <span>Citoyens en attente</span>
                  <span className="badge badge-warning">{stats.citoyens_en_attente ?? 0}</span>
                </div>
                <div className="pending-item">
                  <span>Camioneurs en attente</span>
                  <span className="badge badge-warning">{stats.camioneurs_en_attente ?? 0}</span>
                </div>
              </>
            ) : (
              <div className="spinner-container"><div className="spinner" /></div>
            )}
          </div>
          {(stats?.citoyens_en_attente > 0 || stats?.camioneurs_en_attente > 0) && (
            <div className="flex gap-8 mt-16">
              {stats.citoyens_en_attente > 0 && (
                <Link to="/admin/citoyens" className="btn btn-primary btn-sm">
                  Valider citoyens →
                </Link>
              )}
              {stats.camioneurs_en_attente > 0 && (
                <Link to="/admin/camioneurs" className="btn btn-primary btn-sm">
                  Valider camioneurs →
                </Link>
              )}
            </div>
          )}
        </div>

        <div className="card">
          <div className="flex justify-between items-center mb-16">
            <h2 className="card-title" style={{ margin: 0 }}>Signalements récents (ouverts)</h2>
            <Link to="/admin/signalements" className="btn btn-ghost btn-sm">Voir tout →</Link>
          </div>
          {recentSignalements.length === 0 ? (
            <p className="text-muted text-sm">Aucun signalement ouvert pour le moment.</p>
          ) : (
            <ul className="activity-list">
              {recentSignalements.map((s) => {
                const st = SIG_STATUT[s.statut] || { label: s.statut, cls: 'badge-neutral' };
                return (
                  <li key={s.id} className="activity-item">
                    <div>
                      <strong>{s.type_dechet || 'Déchet'}</strong>
                      <span className="text-muted text-sm"> — {s.citoyen_nom || 'Citoyen'}</span>
                    </div>
                    <span className={`badge ${st.cls}`}>{st.label}</span>
                  </li>
                );
              })}
            </ul>
          )}
          <Link to="/admin/carte" className="btn btn-ghost btn-sm mt-16">
            <MdMap /> Ouvrir la carte GPS →
          </Link>
        </div>
      </div>
    </div>
  );
}
