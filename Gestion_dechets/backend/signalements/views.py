"""
Views — signalements
Mobile citoyen : créer / lister ses signalements
Mobile camioneur : voir signalements proches, accepter, valider, refuser
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from accounts.permissions import IsCitoyenRole, IsCamioneurRole, IsAdminRole
from accounts.models import Camioneur
from .models import Signalement
from .serializers import (
    SignalementSerializer,
    SignalementCreateSerializer,
    SignalementProximiteSerializer,
)
from .utils import get_signalements_proches


# ---------------------------------------------------------------------------
# Mobile Citoyen — Signalements
# ---------------------------------------------------------------------------
class CitoyenSignalementListCreateView(generics.ListCreateAPIView):
    """Liste et création de signalements pour le citoyen connecté."""
    permission_classes = [IsCitoyenRole]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SignalementCreateSerializer
        return SignalementSerializer

    def get_queryset(self):
        return Signalement.objects.filter(
            citoyen=self.request.user.profil_citoyen
        ).order_by('-date_signalement')

    @extend_schema(tags=['Mobile - Citoyen'], summary='Mes signalements')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=['Mobile - Citoyen'], summary='Créer un signalement de déchet')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CitoyenSignalementDetailView(generics.RetrieveAPIView):
    """Détail d'un signalement du citoyen."""
    serializer_class = SignalementSerializer
    permission_classes = [IsCitoyenRole]

    def get_queryset(self):
        return Signalement.objects.filter(citoyen=self.request.user.profil_citoyen)

    @extend_schema(tags=['Mobile - Citoyen'], summary='Détail d\'un signalement')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Mobile Camioneur — Signalements proches
# ---------------------------------------------------------------------------
class CamioneurSignalementsProchesView(APIView):
    """
    Retourne les signalements non traités triés par distance
    depuis la position GPS actuelle du camioneur.
    """
    permission_classes = [IsCamioneurRole]

    @extend_schema(
        tags=['Mobile - Camioneur'],
        summary='Signalements proches (avec carte GPS)',
        parameters=[
            OpenApiParameter('lat', OpenApiTypes.FLOAT, description='Latitude actuelle du camioneur', required=True),
            OpenApiParameter('lng', OpenApiTypes.FLOAT, description='Longitude actuelle du camioneur', required=True),
            OpenApiParameter('rayon', OpenApiTypes.FLOAT, description='Rayon de recherche en km (défaut: 50)', required=False),
        ]
    )
    def get(self, request):
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')

        if not lat or not lng:
            return Response(
                {'error': 'Les paramètres lat et lng sont requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lat = float(lat)
            lng = float(lng)
        except ValueError:
            return Response(
                {'error': 'lat et lng doivent être des nombres décimaux.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        rayon = float(request.query_params.get('rayon', 50))

        # Récupérer uniquement les signalements non assignés
        signalements_qs = Signalement.objects.filter(
            statut='signale'
        ).select_related('citoyen__user')

        # Calculer distances et filtrer par rayon
        resultats = get_signalements_proches(signalements_qs, lat, lng, rayon)

        # Construire la réponse avec distance
        data = []
        for signalement, dist in resultats:
            serializer = SignalementProximiteSerializer(signalement, context={'request': request})
            item = serializer.data
            item['distance_km'] = dist
            data.append(item)

        # Mettre à jour la position du camioneur
        try:
            camioneur = request.user.profil_camioneur
            camioneur.latitude_actuelle = lat
            camioneur.longitude_actuelle = lng
            camioneur.save(update_fields=['latitude_actuelle', 'longitude_actuelle'])
        except Exception:
            pass

        return Response({
            'count': len(data),
            'position_camioneur': {'lat': lat, 'lng': lng},
            'rayon_km': rayon,
            'signalements': data,
        })


class CamioneurAccepterSignalementView(APIView):
    """Le camioneur accepte de collecter un signalement."""
    permission_classes = [IsCamioneurRole]

    @extend_schema(tags=['Mobile - Camioneur'], summary='Accepter un signalement (démarrer collecte)')
    def post(self, request, pk):
        try:
            signalement = Signalement.objects.get(pk=pk, statut='signale')
        except Signalement.DoesNotExist:
            return Response(
                {'error': 'Signalement introuvable ou déjà pris en charge.'},
                status=status.HTTP_404_NOT_FOUND
            )

        camioneur = request.user.profil_camioneur
        if camioneur.statut_inscription != 'accepte':
            return Response(
                {'error': 'Votre compte doit être validé par l\'administrateur.'},
                status=status.HTTP_403_FORBIDDEN
            )

        signalement.statut = 'assigne'
        signalement.camioneur_assigne = camioneur
        signalement.save()

        return Response({
            'message': 'Signalement accepté. Bonne collecte !',
            'signalement_id': signalement.id,
            'coordonnees': {
                'latitude': str(signalement.latitude),
                'longitude': str(signalement.longitude),
            },
            'description': signalement.description,
            'type_dechet': signalement.type_dechet,
        })


class CamioneurValiderSignalementView(APIView):
    """Le camioneur valide qu'il a effectué la collecte."""
    permission_classes = [IsCamioneurRole]

    @extend_schema(tags=['Mobile - Camioneur'], summary='Valider collecte effectuée')
    def post(self, request, pk):
        camioneur = request.user.profil_camioneur
        try:
            signalement = Signalement.objects.get(
                pk=pk,
                camioneur_assigne=camioneur,
                statut__in=['assigne', 'en_cours']
            )
        except Signalement.DoesNotExist:
            return Response(
                {'error': 'Signalement introuvable ou non assigné à vous.'},
                status=status.HTTP_404_NOT_FOUND
            )

        signalement.statut = 'traite'
        signalement.save()

        # Attribuer des éco-points au citoyen signaleur
        if signalement.citoyen:
            signalement.citoyen.solde_eco_points += 5
            signalement.citoyen.save()

        # Attribuer des éco-points au camioneur
        camioneur.solde_eco_points += 5
        camioneur.save(update_fields=['solde_eco_points'])

        return Response({
            'message': 'Collecte validée avec succès. Merci !',
            'signalement_id': signalement.id,
            'statut': 'traite',
        })


class CamioneurRefuserSignalementView(APIView):
    """Le camioneur refuse de collecter un signalement (avec motif)."""
    permission_classes = [IsCamioneurRole]

    @extend_schema(tags=['Mobile - Camioneur'], summary='Refuser une collecte')
    def post(self, request, pk):
        camioneur = request.user.profil_camioneur
        try:
            signalement = Signalement.objects.get(
                pk=pk,
                camioneur_assigne=camioneur,
                statut='assigne'
            )
        except Signalement.DoesNotExist:
            return Response(
                {'error': 'Signalement introuvable ou non assigné à vous.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Libérer le signalement pour un autre camioneur
        signalement.statut = 'signale'
        signalement.camioneur_assigne = None
        signalement.save()

        return Response({
            'message': 'Collecte refusée. Le signalement est de nouveau disponible.',
            'signalement_id': signalement.id,
        })


class CamioneurMesCollectesView(generics.ListAPIView):
    """Historique des collectes du camioneur connecté."""
    serializer_class = SignalementSerializer
    permission_classes = [IsCamioneurRole]

    def get_queryset(self):
        return Signalement.objects.filter(
            camioneur_assigne=self.request.user.profil_camioneur
        ).order_by('-date_modification')

    @extend_schema(tags=['Mobile - Camioneur'], summary='Historique de mes collectes')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Admin — Vue globale des signalements
# ---------------------------------------------------------------------------
class AdminSignalementListView(generics.ListAPIView):
    """Vue admin : tous les signalements avec filtre par statut."""
    serializer_class = SignalementSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        qs = Signalement.objects.select_related(
            'citoyen__user', 'camioneur_assigne__user'
        ).all()
        statut = self.request.query_params.get('statut')
        if statut:
            qs = qs.filter(statut=statut)
        return qs

    @extend_schema(tags=['Admin'], summary='Tous les signalements')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
