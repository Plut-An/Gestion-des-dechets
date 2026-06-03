import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/axiosInstance';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { unwrapList } from '../../utils/api';
import { MdEco, MdPeople, MdCampaign, MdCheckCircle, MdLocalShipping } from 'react-icons/md';

export default function AssoDashboard() {
  const [stats, setStats] = useState(null);
  const { user } = useAuth();
  const toast = useToast();

  useEffect(() => {
    Promise.all([
      api.get('/api/associations/membres/'),
      api.get('/api/associations/adhesions/'),
      api.get('/api/associations/camioneurs/'),
      api.get('/api/mobile/association/evenements/'),
      api.get('/api/mobile/association/annonces/'),
    ])
      .then(([membresRes, adhRes, camRes, evRes, annRes]) => {
        const adhesions = unwrapList(adhRes.data);
        const evenements = unwrapList(evRes.data);
        const annonces = unwrapList(annRes.data);
        const camioneurs = unwrapList(camRes.data);
        setStats({
          membres_acceptes: unwrapList(membresRes.data).length,
          adhesions_attente: adhesions.filter((a) => a.statut === 'en_attente').length,
          camioneurs_acceptes: camioneurs.filter((c) => c.statut === 'accepte').length,
          camioneurs_attente: camioneurs.filter((c) => c.statut === 'en_attente').length,
          total_evenements: evenements.length,
          ev_a_venir: evenements.filter((e) => e.statut === 'a_venir').length,
          total_annonces: annonces.length,
        });
      })
      .catch(() => toast('Impossible de charger le tableau de bord.', 'error'));
  }, [toast]);

  const kpis = [
    {
      icon: <MdPeople />,
      label: 'Membres actifs',
      value: stats?.membres_acceptes,
      color: 'hsl(195, 80%, 50%)',
      sub: `${stats?.adhesions_attente ?? 0} demande(s) en attente`,
      link: '/association/membres',
    },
    {
      icon: <MdEco />,
      label: 'Événements créés',
      value: stats?.total_evenements,
      color: 'hsl(152, 68%, 39%)',
      sub: `${stats?.ev_a_venir ?? 0} à venir`,
      link: '/association/evenements',
    },
    {
      icon: <MdCampaign />,
      label: 'Annonces publiées',
      value: stats?.total_annonces,
      color: 'hsl(271, 60%, 60%)',
      link: '/association/annonces',
    },
    {
      icon: <MdLocalShipping />,
      label: 'Camioneurs liés',
      value: stats?.camioneurs_acceptes,
      color: 'hsl(38, 92%, 55%)',
      sub: `${stats?.camioneurs_attente ?? 0} en attente`,
      link: '/association/camioneurs',
    },
    {
      icon: <MdCheckCircle />,
      label: 'Adhésions à traiter',
      value: stats?.adhesions_attente,
      color: 'hsl(38, 92%, 55%)',
      link: '/association/adhesions',
    },
  ];

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Mon Association</h1>
          <p className="page-subtitle">
            Bienvenue{user?.nom ? `, ${user.nom}` : ''} — espace de gestion
          </p>
        </div>
      </div>

      <div className="kpi-grid">
        {kpis.map((k) => (
          <Link
            key={k.label}
            to={k.link}
            className="kpi-card kpi-card--link"
            style={{ '--kpi-color': k.color, textDecoration: 'none' }}
          >
            <div className="kpi-icon">{k.icon}</div>
            <div className="kpi-body">
              <p className="kpi-value">
                {k.value !== undefined ? k.value : <span className="kpi-skeleton" />}
              </p>
              <p className="kpi-label">{k.label}</p>
              {k.sub && <p className="kpi-sublabel">{k.sub}</p>}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
