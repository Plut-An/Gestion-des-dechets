"""
Permissions personnalisées
"""
from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Autorise uniquement les utilisateurs avec role='admin'."""
    message = "Accès réservé aux administrateurs."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsCitoyenRole(BasePermission):
    """Autorise uniquement les utilisateurs avec role='citoyen'."""
    message = "Accès réservé aux citoyens."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'citoyen'
        )


class IsCamioneurRole(BasePermission):
    """Autorise uniquement les utilisateurs avec role='camioneur'."""
    message = "Accès réservé aux camioneurs."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'camioneur'
        )


class IsAssociationRole(BasePermission):
    """Autorise uniquement les utilisateurs avec role='association'."""
    message = "Accès réservé aux associations."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'association'
        )


class IsAdminOrReadOnly(BasePermission):
    """Admin peut tout faire, les autres peuvent seulement lire."""

    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return request.user and request.user.is_authenticated
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsOwnerOrAdmin(BasePermission):
    """Propriétaire de l'objet ou admin."""

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        # obj peut être un CustomUser, Citoyen ou Camioneur
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user
