"""
Routage API — application core (préfixe global /api/ dans config.urls).

Cartographie cahier des charges ESMIA :
  - login/              → seConnecter() (token DRF)
  - inscription/        → Scénario 1 (justificatifs multipart)
  - signalements/       → Scénario 2 (alertes citoyens + refus chauffeur)
  - evenements/         → Scénario 3 & réseau social éco
  - tournees/optimiser/ → Dashboard admin (Dijkstra vs baseline)
  - profil/me/          → Authentification & profils
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "core"

router = DefaultRouter()
router.register(r"profil", views.ProfilViewSet, basename="profil")
router.register(r"signalements", views.SignalementViewSet, basename="signalement")
router.register(r"evenements", views.EvenementEcologiqueViewSet, basename="evenement")

urlpatterns = [
    # Must — Authentification (seConnecter)
    path("login/", views.ConnexionView.as_view(), name="login"),
    # Scénario 1 — Inscription citoyen
    path("inscription/", views.CitoyenInscriptionView.as_view(), name="inscription"),
    # Rétrocompatibilité
    path("auth/connexion/", views.ConnexionView.as_view(), name="auth-connexion"),
    path("auth/inscription/", views.CitoyenInscriptionView.as_view(), name="auth-inscription"),
    # Dashboard admin — exigences algorithmiques (services.py)
    path(
        "tournees/optimiser/",
        views.OptimisationTourneeView.as_view(),
        name="tournee-optimiser",
    ),
    # Scénario 1 — Validation des inscriptions citoyens
    path(
        "admin/citoyens-enattente/",
        views.CitoyensEnAttenteView.as_view(),
        name="admin-citoyens-enattente",
    ),
    path(
        "admin/valider-citoyen/<int:user_id>/",
        views.ValiderCitoyenView.as_view(),
        name="admin-valider-citoyen",
    ),
    path("", include(router.urls)),
]
