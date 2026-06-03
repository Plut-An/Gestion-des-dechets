"""
Views — associations
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from accounts.permissions import IsAdminRole, IsCitoyenRole, IsAssociationRole
from .models import Association, Adhesion, AcceptationCamioneur
from .serializers import (
    AssociationSerializer,
    AssociationDetailSerializer,
    AssociationCreateSerializer,
    AdhesionSerializer,
    AdhesionCreateSerializer,
    AcceptationCamioneurSerializer,
)


# ---------------------------------------------------------------------------
# Admin — CRUD Associations
# ---------------------------------------------------------------------------
class AdminAssociationListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    queryset = Association.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AssociationCreateSerializer
        return AssociationDetailSerializer

    @extend_schema(tags=['Admin'], summary='Liste des associations')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=['Admin'], summary='Créer une association')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class AdminAssociationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AssociationDetailSerializer
    queryset = Association.objects.all()

    @extend_schema(tags=['Admin'], summary='Détail association')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=['Admin'], summary='Modifier association')
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(tags=['Admin'], summary='Supprimer association')
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Associations — Espace web
# ---------------------------------------------------------------------------
class AssociationListView(generics.ListAPIView):
    """Liste publique des associations (accessible aux citoyens mobile)."""
    serializer_class = AssociationSerializer
    queryset = Association.objects.all()
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Associations'], summary='Liste des associations (public)')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AssociationMembreListView(generics.ListAPIView):
    """Liste des membres (adhésions acceptées) d'une association."""
    serializer_class = AdhesionSerializer
    permission_classes = [IsAssociationRole]

    def get_queryset(self):
        return Adhesion.objects.filter(
            association=self.request.user.profil_association,
            statut='accepte'
        ).select_related('citoyen__user', 'association')

    @extend_schema(tags=['Associations'], summary='Membres d\'une association')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AdhesionListView(generics.ListAPIView):
    """Liste des demandes d'adhésion EN ATTENTE pour une association."""
    serializer_class = AdhesionSerializer
    permission_classes = [IsAssociationRole]

    def get_queryset(self):
        qs = Adhesion.objects.filter(
            association=self.request.user.profil_association,
        ).select_related('citoyen__user', 'association')
        statut = self.request.query_params.get('statut')
        if statut:
            qs = qs.filter(statut=statut)
        return qs

    @extend_schema(tags=['Associations'], summary='Demandes d\'adhésion d\'une association')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AdhesionActionView(APIView):
    """Accepter ou refuser une demande d'adhésion."""
    permission_classes = [IsAssociationRole]

    @extend_schema(tags=['Associations'], summary='Accepter/Refuser une adhésion')
    def post(self, request, adhesion_id):
        try:
            adhesion = Adhesion.objects.get(pk=adhesion_id, association=request.user.profil_association)
        except Adhesion.DoesNotExist:
            return Response({'error': 'Demande introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        motif = request.data.get('motif_refus', '')

        if action == 'accepter':
            adhesion.statut = 'accepte'
            adhesion.save()
            return Response({'message': f'Adhésion de {adhesion.citoyen.user.nom} acceptée.'})
        elif action == 'refuser':
            adhesion.statut = 'refuse'
            adhesion.motif_refus = motif
            adhesion.save()
            return Response({'message': f'Adhésion de {adhesion.citoyen.user.nom} refusée.'})
        else:
            return Response(
                {'error': 'Action invalide. Utilisez "accepter" ou "refuser".'},
                status=status.HTTP_400_BAD_REQUEST
            )


class CamioneurAssociationListView(generics.ListAPIView):
    """Camioneurs liés à une association."""
    serializer_class = AcceptationCamioneurSerializer
    permission_classes = [IsAssociationRole]

    def get_queryset(self):
        qs = AcceptationCamioneur.objects.filter(
            association=self.request.user.profil_association,
        ).select_related('camioneur__user', 'association')
        statut = self.request.query_params.get('statut')
        if statut:
            qs = qs.filter(statut=statut)
        return qs

    @extend_schema(tags=['Associations'], summary='Camioneurs liés à une association')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CamioneurAssociationActionView(APIView):
    """Accepter ou refuser un camioneur pour une association."""
    permission_classes = [IsAssociationRole]

    @extend_schema(tags=['Associations'], summary='Accepter/Refuser un camioneur dans une association')
    def post(self, request, camioneur_id):
        try:
            lien = AcceptationCamioneur.objects.get(
                camioneur_id=camioneur_id,
                association=request.user.profil_association
            )
        except AcceptationCamioneur.DoesNotExist:
            return Response({'error': 'Lien introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        if action == 'accepter':
            lien.statut = 'accepte'
            lien.save()
            return Response({'message': f'Camioneur {lien.camioneur.user.nom} accepté pour {lien.association.nom}.'})
        elif action == 'refuser':
            lien.statut = 'refuse'
            lien.save()
            return Response({'message': f'Camioneur {lien.camioneur.user.nom} refusé.'})
        else:
            return Response(
                {'error': 'Action invalide. Utilisez "accepter" ou "refuser".'},
                status=status.HTTP_400_BAD_REQUEST
            )


# ---------------------------------------------------------------------------
# Mobile — Citoyen : rejoindre une association
# ---------------------------------------------------------------------------
class RejoindreAssociationView(APIView):
    """Un citoyen fait une demande pour rejoindre une association."""
    permission_classes = [IsCitoyenRole]

    @extend_schema(tags=['Mobile - Citoyen'], summary='Demande d\'adhésion à une association')
    def post(self, request, pk):
        try:
            association = Association.objects.get(pk=pk)
        except Association.DoesNotExist:
            return Response({'error': 'Association introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdhesionCreateSerializer(
            data={'association': association.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        adhesion = serializer.save()
        return Response(
            {'message': f'Demande envoyée à {association.nom}. En attente de validation.'},
            status=status.HTTP_201_CREATED
        )
