import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * PrivateRoute — protège une route et vérifie le rôle.
 * @param {string} role - rôle requis ('admin' | 'association')
 */
export default function PrivateRoute({ children, role }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="spinner-container">
        <div className="spinner" />
      </div>
    );
  }

  if (!user) return <Navigate to="/login" replace />;

  if (role && user.role !== role) {
    // Rediriger vers le bon espace selon le rôle réel
    if (user.role === 'admin') return <Navigate to="/admin/dashboard" replace />;
    if (user.role === 'association') return <Navigate to="/association/dashboard" replace />;
    return <Navigate to="/login" replace />;
  }

  return children;
}
