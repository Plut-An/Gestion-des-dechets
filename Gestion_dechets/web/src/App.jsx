import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import PrivateRoute from './routes/PrivateRoute';
import Sidebar from './components/Sidebar/Sidebar';

// Pages publiques
import LandingPage from './pages/Landing/LandingPage';
import LoginPage from './pages/Login/LoginPage';

// Pages Admin
import AdminDashboard   from './pages/admin/AdminDashboard';
import AdminCitoyens    from './pages/admin/AdminCitoyens';
import AdminCamioneurs  from './pages/admin/AdminCamioneurs';
import AdminAssociations from './pages/admin/AdminAssociations';
import AdminCarte          from './pages/admin/AdminCarte';
import AdminSignalements   from './pages/admin/AdminSignalements';

// Pages Association
import AssoDashboard  from './pages/association/AssoDashboard';
import AssoAdhesions  from './pages/association/AssoAdhesions';
import AssoMembres    from './pages/association/AssoMembres';
import AssoCamioneurs from './pages/association/AssoCamioneurs';
import AssoEvenements from './pages/association/AssoEvenements';
import AssoAnnonces   from './pages/association/AssoAnnonces';

import './styles/shared.css';
import './pages/admin/AdminDashboard.css';
import './pages/admin/AdminCarte.css';

/* Layout avec Sidebar pour les espaces protégés */
function AppLayout({ role, children }) {
  return (
    <div className="app-layout">
      <Sidebar role={role} />
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <Routes>
            {/* Route publique */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />

            {/* ─────────────── Portail Administrateur ─────────────── */}
            <Route
              path="/admin/*"
              element={
                <PrivateRoute role="admin">
                  <AppLayout role="admin">
                    <Routes>
                      <Route index element={<Navigate to="dashboard" replace />} />
                      <Route path="dashboard"    element={<AdminDashboard />} />
                      <Route path="citoyens"     element={<AdminCitoyens />} />
                      <Route path="camioneurs"   element={<AdminCamioneurs />} />
                      <Route path="associations" element={<AdminAssociations />} />
                      <Route path="signalements" element={<AdminSignalements />} />
                      <Route path="carte"        element={<AdminCarte />} />
                    </Routes>
                  </AppLayout>
                </PrivateRoute>
              }
            />

            {/* ─────────────── Portail Association ─────────────── */}
            <Route
              path="/association/*"
              element={
                <PrivateRoute role="association">
                  <AppLayout role="association">
                    <Routes>
                      <Route index element={<Navigate to="dashboard" replace />} />
                      <Route path="dashboard"  element={<AssoDashboard />} />
                      <Route path="adhesions"  element={<AssoAdhesions />} />
                      <Route path="membres"    element={<AssoMembres />} />
                      <Route path="camioneurs" element={<AssoCamioneurs />} />
                      <Route path="evenements" element={<AssoEvenements />} />
                      <Route path="annonces"   element={<AssoAnnonces />} />
                    </Routes>
                  </AppLayout>
                </PrivateRoute>
              }
            />

            {/* Redirection par défaut */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
