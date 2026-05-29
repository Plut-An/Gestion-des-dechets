/**
 * Scénario 1 — Validation des inscriptions citoyens (Must — Gestion des inscriptions).
 * Chargé lorsque l'onglet « Validation Inscriptions » est actif.
 */
import { useEffect, useState } from "react";
import { fetchCitoyensEnAttente, validerCitoyen } from "../services/api";

function Spinner() {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16">
      <div
        className="h-10 w-10 animate-spin rounded-full border-4 border-emerald-200 border-t-emerald-600"
        role="status"
        aria-label="Chargement"
      />
      <p className="text-sm text-slate-500">Chargement des inscriptions…</p>
    </div>
  );
}

export default function ValidationInscriptions({ actif }) {
  const [citoyens, setCitoyens] = useState([]);
  const [chargement, setChargement] = useState(false);
  const [erreur, setErreur] = useState("");
  const [succes, setSucces] = useState("");
  const [validationEnCours, setValidationEnCours] = useState(null);

  useEffect(() => {
    if (!actif) return;

    const charger = async () => {
      setChargement(true);
      setErreur("");
      setSucces("");
      try {
        const data = await fetchCitoyensEnAttente();
        setCitoyens(data.resultats || []);
      } catch (err) {
        setErreur(
          err.response?.data?.detail ||
            "Impossible de charger les inscriptions en attente."
        );
        setCitoyens([]);
      } finally {
        setChargement(false);
      }
    };

    charger();
  }, [actif]);

  const handleValider = async (citoyenId) => {
    setValidationEnCours(citoyenId);
    setErreur("");
    setSucces("");
    try {
      const data = await validerCitoyen(citoyenId);
      setSucces(data.message || "Inscription validée avec succès.");
      setCitoyens((prev) => prev.filter((c) => c.id !== citoyenId));
    } catch (err) {
      setErreur(
        err.response?.data?.erreur ||
          err.response?.data?.message ||
          "Échec de la validation."
      );
    } finally {
      setValidationEnCours(null);
    }
  };

  if (chargement) {
    return <Spinner />;
  }

  return (
    <div className="space-y-4">
      {succes && (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
          {succes}
        </div>
      )}
      {erreur && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {erreur}
        </div>
      )}

      {citoyens.length === 0 ? (
        <div className="rounded-xl border border-slate-200 bg-white py-16 text-center shadow-sm">
          <p className="text-lg font-medium text-slate-600">
            Aucune inscription en attente
          </p>
          <p className="mt-1 text-sm text-slate-400">
            Tous les comptes citoyens ont été traités.
          </p>
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Citoyen
                </th>
                <th className="hidden px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500 sm:table-cell">
                  Adresse / contact
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Justificatifs
                </th>
                <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Action
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {citoyens.map((citoyen) => (
                <tr key={citoyen.id} className="hover:bg-slate-50/80">
                  <td className="px-4 py-4">
                    <p className="font-medium text-slate-800">{citoyen.nom}</p>
                    <p className="text-sm text-slate-500">{citoyen.email}</p>
                    <p className="mt-1 text-xs text-slate-400 sm:hidden">
                      {citoyen.adresse}
                    </p>
                  </td>
                  <td className="hidden px-4 py-4 text-sm text-slate-600 sm:table-cell">
                    {citoyen.adresse}
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
                      {citoyen.piece_identite_url ? (
                        <a
                          href={citoyen.piece_identite_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-slate-100"
                        >
                          Voir la pièce d&apos;identité
                        </a>
                      ) : (
                        <span className="text-xs text-slate-400">
                          Pièce d&apos;identité non fournie
                        </span>
                      )}
                      {citoyen.certificat_residence_url ? (
                        <a
                          href={citoyen.certificat_residence_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-slate-100"
                        >
                          Voir le certificat de résidence
                        </a>
                      ) : (
                        <span className="text-xs text-slate-400">
                          Certificat non fourni
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-4 text-right">
                    <button
                      type="button"
                      onClick={() => handleValider(citoyen.id)}
                      disabled={validationEnCours === citoyen.id}
                      className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {validationEnCours === citoyen.id
                        ? "Validation…"
                        : "Valider l'inscription"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
