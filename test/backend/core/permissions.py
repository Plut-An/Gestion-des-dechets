"""
Permissions DRF — contrôle d'accès par rôle métier (cahier des charges ESMIA).

Référence :
  - Citoyen : signalements, likes, commentaires, participation aux événements.
  - Chauffeur : refus de collecte documentés (Scénario 2 — variante refus).
  - Administrateur : dashboard, optimisation des tournées, création d'événements.
"""
from rest_framework.permissions import BasePermission

from .models import Chauffeur, Citoyen, RoleUtilisateur


class IsCitoyen(BasePermission):
    """Utilisateur authentifié possédant un profil Citoyen actif."""

    message = "Accès réservé aux citoyens connectés."

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return Citoyen.objects.filter(pk=request.user.pk, is_active=True).exists()


class IsChauffeur(BasePermission):
    """Utilisateur authentifié possédant un profil Chauffeur."""

    message = "Accès réservé aux chauffeurs."

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return Chauffeur.objects.filter(pk=request.user.pk, is_active=True).exists()


class IsAdministrateur(BasePermission):
    """Administrateur (is_staff ou rôle administrateur)."""

    message = "Accès réservé aux administrateurs."

    def has_permission(self, request, view) -> bool:
        utilisateur = request.user
        return bool(
            utilisateur
            and utilisateur.is_authenticated
            and (
                utilisateur.is_staff
                or utilisateur.role == RoleUtilisateur.ADMINISTRATEUR
            )
        )
