import { useEffect, useState, useCallback } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import api from "../../api/axiosInstance";
import { useToast } from "../../context/ToastContext";
import { unwrapList } from "../../utils/api";
import { MdLocationOn, MdLocalShipping, MdRefresh } from "react-icons/md";
import "leaflet/dist/leaflet.css";
import iconUrl from "leaflet/dist/images/marker-icon.png";
import iconRetinaUrl from "leaflet/dist/images/marker-icon-2x.png";
import shadowUrl from "leaflet/dist/images/marker-shadow.png";
import "./AdminCarte.css";

const defaultIcon = L.icon({
  iconUrl,
  iconRetinaUrl,
  shadowUrl,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28],
});
L.Marker.prototype.options.icon = defaultIcon;

export default function AdminCarte() {
  const [camioneurs, setCamioneurs] = useState([]);
  const [signalements, setSignalements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const toast = useToast();

  const fetchData = useCallback(() => {
    setLoading(true);
    Promise.all([
      api.get("/api/mobile/admin-camioneurs/carte/"),
      api.get("/api/mobile/admin-signalements/"),
    ])
      .then(([camRes, sigRes]) => {
        setCamioneurs(camRes.data.camioneurs || []);
        setSignalements(unwrapList(sigRes.data));
        setLastRefresh(new Date());
      })
      .catch(() => toast("Erreur de chargement des données GPS.", "error"))
      .finally(() => setLoading(false));
  }, [toast]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const formatTime = (d) =>
    d.toLocaleTimeString("fr-FR", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });

  const getMapCenter = (camiones, signales) => {
    const marker =
      camiones.find((c) => c.latitude && c.longitude) ||
      signales.find((s) => s.latitude && s.longitude);
    if (marker) {
      return [parseFloat(marker.latitude), parseFloat(marker.longitude)];
    }
    return [-18.8792, 47.5079];
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Carte de Suivi GPS</h1>
          <p className="page-subtitle">
            Positions en temps réel — dernière mise à jour :{" "}
            {formatTime(lastRefresh)}
          </p>
        </div>
        <button
          className="btn btn-ghost"
          onClick={fetchData}
          disabled={loading}
        >
          <MdRefresh className={loading ? "spin-icon" : ""} /> Actualiser
        </button>
      </div>

      <div className="map-frame card">
        {loading ? (
          <div className="spinner-container">
            <div className="spinner" />
          </div>
        ) : camioneurs.length === 0 &&
          signalements.filter((s) => s.statut === "signale").length === 0 ? (
          <div className="carte-inner">
            <span className="carte-emoji">🗺️</span>
            <p className="carte-title">Aucune position GPS disponible</p>
            <p className="carte-desc">
              Aucune donnée de camioneur ou signalement ouvert n'est disponible
              pour l'instant.
            </p>
          </div>
        ) : (
          <MapContainer
            center={getMapCenter(camioneurs, signalements)}
            zoom={12}
            scrollWheelZoom={true}
            className="leaflet-container"
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {camioneurs.map((c) =>
              c.latitude && c.longitude ? (
                <Marker
                  key={`cam-${c.id}`}
                  position={[parseFloat(c.latitude), parseFloat(c.longitude)]}
                >
                  <Popup>
                    <strong>{c.nom}</strong>
                    <br />
                    {c.disponible ? "Disponible" : "Occupé"}
                    <br />
                    {parseFloat(c.latitude).toFixed(5)},{" "}
                    {parseFloat(c.longitude).toFixed(5)}
                  </Popup>
                </Marker>
              ) : null,
            )}
            {signalements
              .filter((s) => s.statut === "signale")
              .map((s) => (
                <Marker
                  key={`sig-${s.id}`}
                  position={[parseFloat(s.latitude), parseFloat(s.longitude)]}
                >
                  <Popup>
                    <strong>{s.type_dechet || "Signalement"}</strong>
                    <br />
                    {parseFloat(s.latitude).toFixed(5)},{" "}
                    {parseFloat(s.longitude).toFixed(5)}
                  </Popup>
                </Marker>
              ))}
          </MapContainer>
        )}
      </div>

      <div className="carte-grid">
        {/* Camioneurs */}
        <div className="card">
          <div className="flex items-center gap-8 mb-16">
            <MdLocalShipping
              style={{ color: "var(--color-primary-light)", fontSize: 22 }}
            />
            <h2 className="card-title" style={{ margin: 0 }}>
              Camioneurs disponibles (
              {camioneurs.filter((c) => c.disponible).length})
            </h2>
          </div>
          {loading ? (
            <div className="spinner-container">
              <div className="spinner" />
            </div>
          ) : camioneurs.length === 0 ? (
            <p className="text-muted text-sm">
              Aucun camioneur avec une position GPS.
            </p>
          ) : (
            <div className="gps-list">
              {camioneurs.map((c) => (
                <div
                  key={c.id}
                  className={`gps-item ${c.disponible ? "gps-item--active" : ""}`}
                >
                  <div
                    className="gps-dot"
                    style={{
                      background: c.disponible
                        ? "var(--color-primary)"
                        : "var(--text-muted)",
                    }}
                  />
                  <div className="gps-info">
                    <p className="gps-name">{c.nom}</p>
                    <p className="gps-coords">
                      {parseFloat(c.latitude).toFixed(5)},{" "}
                      {parseFloat(c.longitude).toFixed(5)}
                    </p>
                  </div>
                  <span
                    className={`badge ${c.disponible ? "badge-success" : "badge-neutral"}`}
                  >
                    {c.disponible ? "Disponible" : "Occupé"}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Signalements ouverts */}
        <div className="card">
          <div className="flex items-center gap-8 mb-16">
            <MdLocationOn
              style={{ color: "var(--color-warning)", fontSize: 22 }}
            />
            <h2 className="card-title" style={{ margin: 0 }}>
              Signalements ouverts (
              {signalements.filter((s) => s.statut === "signale").length})
            </h2>
          </div>
          {loading ? (
            <div className="spinner-container">
              <div className="spinner" />
            </div>
          ) : signalements.length === 0 ? (
            <p className="text-muted text-sm">Aucun signalement ouvert.</p>
          ) : (
            <div className="gps-list">
              {signalements
                .filter((s) => s.statut === "signale")
                .slice(0, 10)
                .map((s) => (
                  <div key={s.id} className="gps-item">
                    <div
                      className="gps-dot"
                      style={{ background: "var(--color-warning)" }}
                    />
                    <div className="gps-info">
                      <p className="gps-name">
                        {s.type_dechet || "Déchet signalé"}
                      </p>
                      <p className="gps-coords">
                        {parseFloat(s.latitude).toFixed(5)},{" "}
                        {parseFloat(s.longitude).toFixed(5)}
                      </p>
                    </div>
                    <span className="badge badge-warning">Ouvert</span>
                  </div>
                ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
