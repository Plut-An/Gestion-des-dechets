/**
 * Application web administrateur — routage simple par état d'authentification.
 */
import { useState } from "react";
import LoginAdmin from "./components/LoginAdmin";
import DashboardAdmin from "./pages/DashboardAdmin";
import { isAuthenticated } from "./services/api";

export default function App() {
  const [connecte, setConnecte] = useState(isAuthenticated);

  return connecte ? (
    <DashboardAdmin onLogout={() => setConnecte(false)} />
  ) : (
    <LoginAdmin onLoginSuccess={() => setConnecte(true)} />
  );
}
