import React from 'react';
import { Link } from 'react-router-dom';
import { MdEco, MdLocalShipping, MdGroups, MdArrowForward } from 'react-icons/md';
import './LandingPage.css';

export default function LandingPage() {
  return (
    <div className="landing-page">
      {/* Navigation */}
      <nav className="landing-nav">
        <div className="landing-logo">
          <span>🌿</span> ÉcoGestion
        </div>
        <div className="landing-nav-links">
          <Link to="/login" className="landing-login-btn">Se connecter</Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="landing-hero">
        <div className="landing-hero-content">
          <h1 className="landing-hero-title">
            Ensemble pour une ville <span>plus propre</span> et durable.
          </h1>
          <p className="landing-hero-subtitle">
            ÉcoGestion est la plateforme citoyenne qui vous permet de signaler les déchets, participer à des événements écologiques, et gagner des récompenses pour vos actions.
          </p>
          <Link to="/login" className="landing-hero-cta">
            Rejoindre le mouvement <MdArrowForward size={24} />
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="landing-features">
        <h2 className="landing-section-title">Comment ça marche ?</h2>
        <div className="features-grid">
          
          <div className="feature-card">
            <div className="feature-icon-wrapper">
              <MdEco />
            </div>
            <h3 className="feature-title">Signaler & Nettoyer</h3>
            <p className="feature-desc">
              Prenez en photo les déchets abandonnés. Nos camioneurs partenaires se chargeront de la collecte et vous gagnerez des Éco-points.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon-wrapper">
              <MdGroups />
            </div>
            <h3 className="feature-title">S'engager en Communauté</h3>
            <p className="feature-desc">
              Rejoignez des associations locales, participez à des événements de nettoyage collectif et faites briller votre ville.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon-wrapper">
              <MdLocalShipping />
            </div>
            <h3 className="feature-title">Collecte Optimisée</h3>
            <p className="feature-desc">
              Vous êtes camioneur ? Trouvez facilement les signalements proches de vous sur une carte interactive et optimisez vos trajets.
            </p>
          </div>

        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <p>&copy; {new Date().getFullYear()} ÉcoGestion. Tous droits réservés.</p>
      </footer>
    </div>
  );
}
