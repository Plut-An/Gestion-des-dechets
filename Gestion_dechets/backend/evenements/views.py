"""
Views — evenements (annonces, événements écologiques, participations)
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from accounts.permissions import IsAdminRole, IsCitoyenRole, IsAssociationRole
from .models import Annonce, EvenementEcologique, Participation, Commentaire
from .serializers import AnnonceSerializer, EvenementSerializer, ParticipationSerializer, CommentaireSerializer


# ---------------------------------------------------------------------------
# Annonces — gestion par association (web admin)
# ---------------------------------------------------------------------------
class AnnonceListCreateView(generics.ListCreateAPIView):
    serializer_class = AnnonceSerializer
    permission_classes = [IsAssociationRole]

    def get_queryset(self):
        return Annonce.objects.filter(
            association=self.request.user.profil_association
        ).select_related('association')

    def perform_create(self, serializer):
        serializer.save(association=self.request.user.profil_association)

    @extend_schema(tags=['Associations'], summary='Liste des annonces d\'une association')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=['Associations'], summary='Publier une annonce')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class AnnonceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AnnonceSerializer
    permission_classes = [IsAssociationRole]

    def get_queryset(self):
        return Annonce.objects.filter(association=self.request.user.profil_association)

    @extend_schema(tags=['Associations'], summary='Détail annonce')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=['Associations'], summary='Modifier annonce')
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(tags=['Associations'], summary='Supprimer annonce')
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Événements — gestion par association (web admin)
# ---------------------------------------------------------------------------
class EvenementListCreateView(generics.ListCreateAPIView):
    serializer_class = EvenementSerializer
    permission_classes = [IsAssociationRole]

    def get_queryset(self):
        return EvenementEcologique.objects.filter(
            association=self.request.user.profil_association
        ).select_related('association')

    def perform_create(self, serializer):
        serializer.save(association=self.request.user.profil_association)

    @extend_schema(tags=['Associations'], summary='Liste des événements d\'une association')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=['Associations'], summary='Créer un événement')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class EvenementDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EvenementSerializer
    permission_classes = [IsAssociationRole]

    def get_queryset(self):
        return EvenementEcologique.objects.filter(association=self.request.user.profil_association)

    @extend_schema(tags=['Associations'], summary='Détail événement')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=['Associations'], summary='Modifier événement')
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(tags=['Associations'], summary='Supprimer événement')
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class EvenementParticipantsView(generics.ListAPIView):
    """Liste des participants à un événement (pour l'association — feuille de présence)."""
    serializer_class = ParticipationSerializer
    permission_classes = [IsAssociationRole]

    def get_queryset(self):
        return Participation.objects.filter(
            evenement_id=self.kwargs['ev_pk'],
            evenement__association=self.request.user.profil_association,
        ).select_related('citoyen__user', 'evenement')

    @extend_schema(tags=['Associations'], summary='Liste des participants à un événement')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ConfirmerPresenceView(APIView):
    """L'association confirme la présence d'un citoyen à l'événement."""
    permission_classes = [IsAssociationRole]

    @extend_schema(tags=['Associations'], summary='Confirmer présence d\'un participant')
    def post(self, request, ev_pk, participation_id):
        try:
            participation = Participation.objects.get(
                pk=participation_id,
                evenement_id=ev_pk,
                evenement__association=request.user.profil_association,
            )
        except Participation.DoesNotExist:
            return Response({'error': 'Participation introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        participation.presence_confirmee = True
        participation.save()

        # Attribuer des éco-points au citoyen
        citoyen = participation.citoyen
        citoyen.solde_eco_points += 10  # 10 points par présence confirmée
        citoyen.save()

        return Response({
            'message': f'Présence de {citoyen.user.nom} confirmée. +10 éco-points attribués.',
            'eco_points_total': citoyen.solde_eco_points,
        })


# ---------------------------------------------------------------------------
# Mobile — Flux public événements & annonces
# ---------------------------------------------------------------------------
class MobileEvenementListView(generics.ListAPIView):
    """Tous les événements à venir — pour les citoyens mobile."""
    serializer_class = EvenementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EvenementEcologique.objects.filter(
            statut__in=['a_venir', 'en_cours']
        ).select_related('association').order_by('date_evenement')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    @extend_schema(tags=['Mobile - Citoyen'], summary='Événements disponibles (mobile)')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MobileAnnonceListView(generics.ListAPIView):
    """Flux d'annonces de toutes les associations — pour les citoyens mobile."""
    serializer_class = AnnonceSerializer
    permission_classes = [IsAuthenticated]
    queryset = Annonce.objects.select_related('association').order_by('-date_publication')

    @extend_schema(tags=['Mobile - Citoyen'], summary='Flux d\'annonces (mobile)')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ParticiperEvenementView(APIView):
    """Un citoyen s'inscrit à un événement ou annule sa participation."""
    permission_classes = [IsCitoyenRole]

    @extend_schema(tags=['Mobile - Citoyen'], summary='Participer à un événement')
    def post(self, request, ev_pk):
        try:
            evenement = EvenementEcologique.objects.get(pk=ev_pk, statut__in=['a_venir', 'en_cours'])
        except EvenementEcologique.DoesNotExist:
            return Response(
                {'error': 'Événement introuvable ou terminé.'},
                status=status.HTTP_404_NOT_FOUND
            )

        citoyen = request.user.profil_citoyen
        participation, created = Participation.objects.get_or_create(
            citoyen=citoyen, evenement=evenement
        )

        if created:
            return Response(
                {'message': f'Vous participez à "{evenement.titre}". À bientôt !'},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'message': 'Vous participez déjà à cet événement.'},
            status=status.HTTP_200_OK
        )

    @extend_schema(tags=['Mobile - Citoyen'], summary='Annuler sa participation')
    def delete(self, request, ev_pk):
        try:
            citoyen = request.user.profil_citoyen
            participation = Participation.objects.get(
                citoyen=citoyen, evenement_id=ev_pk
            )
            participation.delete()
            return Response({'message': 'Participation annulée.'}, status=status.HTTP_200_OK)
        except Participation.DoesNotExist:
            return Response({'error': 'Vous ne participez pas à cet événement.'}, status=status.HTTP_404_NOT_FOUND)


class MesParticipationsView(generics.ListAPIView):
    """Mes participations — citoyen mobile."""
    serializer_class = ParticipationSerializer
    permission_classes = [IsCitoyenRole]

    def get_queryset(self):
        return Participation.objects.filter(
            citoyen=self.request.user.profil_citoyen
        ).select_related('evenement__association')

    @extend_schema(tags=['Mobile - Citoyen'], summary='Mes participations')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CommentaireListCreateView(generics.ListCreateAPIView):
    """
    Commentaires sur un événement écologique.
    - GET : Liste des commentaires (ouverte à tous).
    - POST : Ajouter un commentaire (réservé aux membres acceptés et à l'admin de l'asso).
    """
    serializer_class = CommentaireSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Commentaire.objects.filter(
            evenement_id=self.kwargs['ev_pk']
        ).select_related('auteur').order_by('date_publication')

    def perform_create(self, serializer):
        from rest_framework.exceptions import PermissionDenied
        from associations.models import Adhesion
        evenement = EvenementEcologique.objects.get(pk=self.kwargs['ev_pk'])
        user = self.request.user

        is_admin_asso = False
        if hasattr(user, 'profil_association'):
            is_admin_asso = (evenement.association == user.profil_association)

        is_membre_accepte = False
        
        if hasattr(user, 'profil_citoyen'):
            is_membre_accepte = Adhesion.objects.filter(
                association=evenement.association,
                citoyen=user.profil_citoyen,
                statut='accepte'
            ).exists()

        if not (is_admin_asso or is_membre_accepte):
            raise PermissionDenied("Seuls les membres de l'association peuvent commenter cet événement.")

        serializer.save(evenement=evenement, auteur=user)

    @extend_schema(tags=['Mobile - Citoyen'], summary='Liste et ajout de commentaires (GET/POST)')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=['Mobile - Citoyen'], summary='Ajouter un commentaire')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CommentaireDeleteView(generics.DestroyAPIView):
    """Supprimer un commentaire (Auteur ou Admin asso)."""
    serializer_class = CommentaireSerializer
    permission_classes = [IsAuthenticated]
    queryset = Commentaire.objects.all()

    def perform_destroy(self, instance):
        from rest_framework.exceptions import PermissionDenied
        user = self.request.user
        
        is_admin_asso = False
        if hasattr(user, 'profil_association'):
            is_admin_asso = (instance.evenement.association == user.profil_association)
            
        if instance.auteur != user and not is_admin_asso:
            raise PermissionDenied("Vous n'êtes pas autorisé à supprimer ce commentaire.")
        instance.delete()

    @extend_schema(tags=['Mobile - Citoyen'], summary='Supprimer un commentaire')
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
