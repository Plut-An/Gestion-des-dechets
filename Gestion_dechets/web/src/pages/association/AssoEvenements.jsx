import { useEffect, useState, useCallback } from 'react';
import api from '../../api/axiosInstance';
import { useToast } from '../../context/ToastContext';
import { unwrapList, toApiDateTime, getErrorMessage } from '../../utils/api';
import { MdAdd, MdClose, MdPeople, MdCheckCircle, MdDelete, MdEdit } from 'react-icons/md';

const STATUT_EV = {
  a_venir: { text: 'À venir', cls: 'badge-accent' },
  en_cours: { text: 'En cours', cls: 'badge-warning' },
  termine: { text: 'Terminé', cls: 'badge-neutral' },
  annule: { text: 'Annulé', cls: 'badge-danger' },
};

const EMPTY_FORM = {
  titre: '', description: '', date_evenement: '', lieu: '', statut: 'a_venir',
};

function toLocalDateTime(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '';
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export default function AssoEvenements() {
  const [evenements, setEvenements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingEv, setEditingEv] = useState(null);
  const [selectedEv, setSelectedEv] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const toast = useToast();

  const fetchEvenements = useCallback(() => {
    setLoading(true);
    api.get('/api/mobile/association/evenements/')
      .then((res) => setEvenements(unwrapList(res.data)))
      .catch(() => toast('Erreur lors du chargement.', 'error'))
      .finally(() => setLoading(false));
  }, [toast]);

  useEffect(() => { fetchEvenements(); }, [fetchEvenements]);

  const openCreate = () => {
    setEditingEv(null);
    setForm(EMPTY_FORM);
    setShowModal(true);
  };

  const openEdit = (ev) => {
    setEditingEv(ev);
    setForm({
      titre: ev.titre || '',
      description: ev.description || '',
      date_evenement: toLocalDateTime(ev.date_evenement),
      lieu: ev.lieu || '',
      statut: ev.statut || 'a_venir',
    });
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.titre || !form.date_evenement || !form.lieu) {
      toast('Titre, date et lieu sont requis.', 'warning');
      return;
    }
    setSaving(true);
    const payload = {
      ...form,
      date_evenement: toApiDateTime(form.date_evenement),
    };
    try {
      if (editingEv) {
        await api.put(`/api/mobile/association/evenements/${editingEv.id}/`, payload);
        toast('Événement mis à jour.', 'success');
      } else {
        await api.post('/api/mobile/association/evenements/', payload);
        toast('Événement créé !', 'success');
      }
      setShowModal(false);
      setForm(EMPTY_FORM);
      setEditingEv(null);
      fetchEvenements();
    } catch (err) {
      toast(getErrorMessage(err, 'Erreur de sauvegarde.'), 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Supprimer cet événement ?')) return;
    try {
      await api.delete(`/api/mobile/association/evenements/${id}/`);
      toast('Événement supprimé.', 'success');
      fetchEvenements();
    } catch (err) {
      toast(getErrorMessage(err, 'Suppression impossible.'), 'error');
    }
  };

  const openParticipants = async (ev) => {
    setSelectedEv(ev);
    try {
      const res = await api.get(`/api/mobile/association/evenements/${ev.id}/participants/`);
      setParticipants(unwrapList(res.data));
    } catch {
      toast('Impossible de charger les participants.', 'error');
      setParticipants([]);
    }
  };

  const confirmerPresence = async (partId) => {
    try {
      const res = await api.post(
        `/api/mobile/association/evenements/${selectedEv.id}/participants/${partId}/confirmer/`,
      );
      toast(res.data?.message || '+10 éco-points attribués !', 'success');
      openParticipants(selectedEv);
    } catch (err) {
      toast(getErrorMessage(err, 'Erreur lors de la confirmation.'), 'error');
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Événements Écologiques</h1>
          <p className="page-subtitle">Créez et gérez vos événements</p>
        </div>
        <button type="button" className="btn btn-primary" onClick={openCreate}>
          <MdAdd /> Nouvel événement
        </button>
      </div>

      {loading ? (
        <div className="spinner-container"><div className="spinner" /></div>
      ) : evenements.length === 0 ? (
        <div className="empty-state card">
          <span style={{ fontSize: 48 }}>🌱</span>
          <p>Aucun événement créé. Commencez par en créer un !</p>
        </div>
      ) : (
        <div className="evenements-grid">
          {evenements.map((ev) => {
            const s = STATUT_EV[ev.statut] || { text: ev.statut, cls: 'badge-neutral' };
            return (
              <div key={ev.id} className="card evenement-card">
                <div className="flex justify-between items-center mb-16">
                  <span className={`badge ${s.cls}`}>{s.text}</span>
                  <span className="text-muted text-sm">
                    {new Date(ev.date_evenement).toLocaleDateString('fr-FR', {
                      day: '2-digit', month: 'long', year: 'numeric',
                    })}
                  </span>
                </div>
                <h3 className="evenement-title">{ev.titre}</h3>
                <p className="evenement-lieu">📍 {ev.lieu}</p>
                <p className="text-sm text-muted mb-8">
                  {ev.compteur_volontaires ?? 0} inscrit(s) · {ev.compteur_presents ?? 0} présent(s)
                </p>
                {ev.description && <p className="evenement-desc">{ev.description}</p>}
                <div className="flex gap-8 mt-16 flex-wrap">
                  <button type="button" className="btn btn-ghost btn-sm" onClick={() => openParticipants(ev)}>
                    <MdPeople /> Présence
                  </button>
                  <button type="button" className="btn btn-ghost btn-sm" onClick={() => openEdit(ev)}>
                    <MdEdit /> Modifier
                  </button>
                  <button type="button" className="btn btn-danger btn-sm" onClick={() => handleDelete(ev.id)}>
                    <MdDelete />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">{editingEv ? 'Modifier l\'événement' : 'Créer un événement'}</h2>
              <button type="button" className="modal-close" onClick={() => setShowModal(false)}><MdClose /></button>
            </div>
            <form className="modal-form" onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Titre *</label>
                <input className="form-input" value={form.titre} onChange={(e) => setForm({ ...form, titre: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Lieu *</label>
                <input className="form-input" value={form.lieu} onChange={(e) => setForm({ ...form, lieu: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Date et heure *</label>
                <input type="datetime-local" className="form-input" value={form.date_evenement}
                  onChange={(e) => setForm({ ...form, date_evenement: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Statut</label>
                <select className="form-input" value={form.statut} onChange={(e) => setForm({ ...form, statut: e.target.value })}>
                  <option value="a_venir">À venir</option>
                  <option value="en_cours">En cours</option>
                  <option value="termine">Terminé</option>
                  <option value="annule">Annulé</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea className="form-input" value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })} />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-ghost" onClick={() => setShowModal(false)}>Annuler</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? 'Enregistrement...' : editingEv ? 'Enregistrer' : 'Créer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {selectedEv && (
        <div className="modal-overlay" onClick={() => setSelectedEv(null)}>
          <div className="modal" style={{ maxWidth: 620 }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Présence — {selectedEv.titre}</h2>
              <button type="button" className="modal-close" onClick={() => setSelectedEv(null)}><MdClose /></button>
            </div>
            {participants.length === 0 ? (
              <p className="text-muted text-sm" style={{ textAlign: 'center', padding: '24px 0' }}>
                Aucun participant inscrit.
              </p>
            ) : (
              <table className="data-table" style={{ marginTop: 0 }}>
                <thead>
                  <tr><th>Citoyen</th><th>Email</th><th>Présence</th><th>Action</th></tr>
                </thead>
                <tbody>
                  {participants.map((p) => (
                    <tr key={p.id}>
                      <td><strong>{p.citoyen_nom || '—'}</strong></td>
                      <td className="text-sm">{p.citoyen_email}</td>
                      <td>
                        <span className={`badge ${p.presence_confirmee ? 'badge-success' : 'badge-neutral'}`}>
                          {p.presence_confirmee ? 'Confirmée' : 'En attente'}
                        </span>
                      </td>
                      <td>
                        {!p.presence_confirmee ? (
                          <button type="button" className="btn btn-success btn-sm" onClick={() => confirmerPresence(p.id)}>
                            <MdCheckCircle /> +10 pts
                          </button>
                        ) : (
                          <span className="text-muted text-sm">✓</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
