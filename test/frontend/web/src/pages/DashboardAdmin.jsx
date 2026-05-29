/**
 * Dashboard administrateur — Must (cahier des charges : Dashboard).
 */
import { useState } from "react";
import ValidationInscriptions from "../components/ValidationInscriptions";
import { clearStoredToken } from "../services/api";

const ONGLETS = [
  { id: "validation", label: "Validation Inscriptions" },
  { id: "optimisation", label: "Optimisation Dijkstra" },
  { id: "statistiques", label: "Statistiques" },
];

export default function DashboardAdmin({ onLogout }) {
  const [ongletActif, setOngletActif] = useState("validation");

  const handleLogout = () => {
    clearStoredToken();
    onLogout?.();
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white px-6 py-4 shadow-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-emerald-800">
              Tableau de bord — Administration
            </h1>
            <p className="text-sm text-slate-500">
              Plateforme de collecte et d&apos;optimisation des déchets urbains
            </p>
          </div>
          <button
            type="button"
            onClick={handleLogout}
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
          >
            Déconnexion
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-6xl p-6">
        <nav className="mb-6 flex flex-wrap gap-2 border-b border-slate-200 pb-4">
          {ONGLETS.map((onglet) => (
            <button
              key={onglet.id}
              type="button"
              onClick={() => setOngletActif(onglet.id)}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                ongletActif === onglet.id
                  ? "bg-emerald-600 text-white shadow-sm"
                  : "bg-white text-slate-600 ring-1 ring-slate-200 hover:bg-slate-50"
              }`}
            >
              {onglet.label}
            </button>
          ))}
        </nav>

        {ongletActif === "validation" && (
          <section>
            <h2 className="mb-4 text-lg font-semibold text-amber-900">
              Validation des citoyens
            </h2>
            <p className="mb-6 text-sm text-slate-500">
              Scénario 1 — Vérification des pièces jointes et activation des
              comptes en attente.
            </p>
            <ValidationInscriptions actif={ongletActif === "validation"} />
          </section>
        )}

        {ongletActif === "optimisation" && (
          <section className="rounded-xl border border-dashed border-emerald-300 bg-emerald-50/50 p-6">
            <h2 className="text-lg font-semibold text-emerald-900">
              Optimisation des tournées (Dijkstra)
            </h2>
            <p className="mt-2 text-sm text-emerald-800/80">
              À implémenter — rapport comparatif via POST /api/tournees/optimiser/.
            </p>
          </section>
        )}

        {ongletActif === "statistiques" && (
          <section className="rounded-xl border border-dashed border-blue-300 bg-blue-50/50 p-6">
            <h2 className="text-lg font-semibold text-blue-900">Statistiques</h2>
            <p className="mt-2 text-sm text-blue-800/80">
              À implémenter — tonnage collecté, taux de recyclage, cartographie.
            </p>
          </section>
        )}
      </main>
    </div>
  );
}
