import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import './Login.css';

export default function LoginPage() {
  const [email, setEmail]     = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const toast     = useToast();
  const navigate  = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      toast('Veuillez remplir tous les champs.', 'warning');
      return;
    }
    setLoading(true);
    try {
      const user = await login(email, password);
      toast(`Bienvenue, ${user.nom} !`, 'success');
      if (user.role === 'admin') navigate('/admin/dashboard');
      else if (user.role === 'association') navigate('/association/dashboard');
      else navigate('/login'); // autre rôle non géré par le web
    } catch (err) {
      const data = err.response?.data;
      const msg = data?.detail
        || (data && typeof data === 'object' && Object.values(data).flat?.()[0])
        || 'Identifiants incorrects.';
      toast(String(msg), 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-bg" />

      <div className="login-card">
        <div className="login-header">
          <span className="login-logo">🌿</span>
          <h1 className="login-title">ÉcoGestion</h1>
          <p className="login-subtitle">Plateforme de gestion des déchets</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label className="form-label" htmlFor="email">Adresse e-mail</label>
            <input
              id="email"
              type="email"
              className="form-input"
              placeholder="admin@dechets.mg"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              autoFocus
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">Mot de passe</label>
            <input
              id="password"
              type="password"
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary w-full login-btn"
            disabled={loading}
          >
            {loading ? <span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} /> : null}
            {loading ? 'Connexion...' : 'Se connecter'}
          </button>
        </form>

        <p className="login-footer">
          Gestion des déchets & écologie — Madagascar 🌍
        </p>
      </div>
    </div>
  );
}
