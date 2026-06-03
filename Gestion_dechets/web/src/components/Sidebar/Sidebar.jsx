import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import {
  MdDashboard, MdPeople, MdLocalShipping, MdApartment,
  MdLogout, MdEco, MdMap, MdWarning, MdGroups
} from 'react-icons/md';
import './Sidebar.css';

const ADMIN_LINKS = [
  { to: '/admin/dashboard',    icon: <MdDashboard />,     label: 'Tableau de bord' },
  { to: '/admin/citoyens',     icon: <MdPeople />,        label: 'Citoyens' },
  { to: '/admin/camioneurs',   icon: <MdLocalShipping />, label: 'Camioneurs' },
  { to: '/admin/associations', icon: <MdApartment />,     label: 'Associations' },
  { to: '/admin/signalements', icon: <MdWarning />,       label: 'Signalements' },
  { to: '/admin/carte',        icon: <MdMap />,           label: 'Carte GPS' },
];

const ASSO_LINKS = [
  { to: '/association/dashboard',  icon: <MdDashboard />,     label: 'Tableau de bord' },
  { to: '/association/adhesions',  icon: <MdPeople />,        label: 'Adhésions' },
  { to: '/association/membres',    icon: <MdGroups />,        label: 'Membres' },
  { to: '/association/camioneurs', icon: <MdLocalShipping />, label: 'Camioneurs' },
  { to: '/association/evenements', icon: <MdEco />,           label: 'Événements' },
  { to: '/association/annonces',   icon: <MdApartment />,     label: 'Annonces' },
];

export default function Sidebar({ role }) {
  const { user, logout } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const links = role === 'admin' ? ADMIN_LINKS : ASSO_LINKS;

  const handleLogout = async () => {
    await logout();
    toast('Vous êtes déconnecté.', 'success');
    navigate('/login');
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <span className="sidebar-logo-icon">🌿</span>
        <div>
          <p className="sidebar-logo-title">ÉcoGestion</p>
          <p className="sidebar-logo-role">
            {role === 'admin' ? 'Administrateur' : 'Association'}
          </p>
        </div>
      </div>

      <nav className="sidebar-nav">
        {links.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `sidebar-link ${isActive ? 'sidebar-link--active' : ''}`
            }
          >
            <span className="sidebar-link-icon">{icon}</span>
            <span className="sidebar-link-label">{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="sidebar-avatar">
            {user?.nom?.[0]?.toUpperCase() || '?'}
          </div>
          <div className="sidebar-user-info">
            <p className="sidebar-user-name">{user?.nom}</p>
            <p className="sidebar-user-email">{user?.email}</p>
          </div>
        </div>
        <button className="sidebar-logout" onClick={handleLogout} title="Déconnexion">
          <MdLogout />
        </button>
      </div>
    </aside>
  );
}
