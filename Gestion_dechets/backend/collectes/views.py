"""
Views — collectes (position GPS camioneur)
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from accounts.permissions import IsCamioneurRole, IsAdminRole
from accounts.models import Camioneur
from .models import PositionCamioneur
from .serializers import PositionCamioneurSerializer, MettreAJourPositionSerializer


class MettreAJourPositionView(APIView):
    """
    Le camioneur met à jour sa position GPS en temps réel.
    Enregistre dans l'historique et met à jour la position courante.
    """
    permission_classes = [IsCamioneurRole]

    @extend_schema(
        tags=['Mobile - Camioneur'],
        summary='Mettre à jour ma position GPS',
        request=MettreAJourPositionSerializer,
    )
    def put(self, request):
        serializer = MettreAJourPositionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        camioneur = request.user.profil_camioneur
        lat = serializer.validated_data['latitude']
        lng = serializer.validated_data['longitude']

        # Mettre à jour position actuelle sur le profil
        camioneur.latitude_actuelle = lat
        camioneur.longitude_actuelle = lng
        if 'disponible' in serializer.validated_data:
            camioneur.disponible = serializer.validated_data['disponible']
        camioneur.save(update_fields=['latitude_actuelle', 'longitude_actuelle', 'disponible'])

        # Enregistrer dans l'historique GPS
        PositionCamioneur.objects.create(
            camioneur=camioneur,
            latitude=lat,
            longitude=lng,
        )

        # Purger les anciens enregistrements (garder 500 max par camioneur)
        ids_a_garder = PositionCamioneur.objects.filter(
            camioneur=camioneur
        ).order_by('-horodatage').values_list('id', flat=True)[:500]
        PositionCamioneur.objects.filter(
            camioneur=camioneur
        ).exclude(id__in=list(ids_a_garder)).delete()

        return Response({
            'message': 'Position mise à jour.',
            'latitude': str(lat),
            'longitude': str(lng),
            'disponible': camioneur.disponible,
        })


class HistoriquePositionView(generics.ListAPIView):
    """Historique des 50 dernières positions GPS du camioneur connecté."""
    serializer_class = PositionCamioneurSerializer
    permission_classes = [IsCamioneurRole]

    def get_queryset(self):
        return PositionCamioneur.objects.filter(
            camioneur=self.request.user.profil_camioneur
        ).order_by('-horodatage')[:50]

    @extend_schema(tags=['Mobile - Camioneur'], summary='Historique de mes positions GPS')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProfilCamioneurView(APIView):
    """Profil complet du camioneur connecté."""
    permission_classes = [IsCamioneurRole]

    @extend_schema(tags=['Mobile - Camioneur'], summary='Mon profil camioneur')
    def get(self, request):
        from accounts.serializers import CamioneurDetailSerializer
        camioneur = request.user.profil_camioneur
        serializer = CamioneurDetailSerializer(camioneur)
        return Response(serializer.data)

    @extend_schema(tags=['Mobile - Camioneur'], summary='Modifier mon profil')
    def patch(self, request):
        camioneur = request.user.profil_camioneur
        user = request.user

        # Mettre à jour nom et langue
        if 'nom' in request.data:
            user.nom = request.data['nom']
        if 'langue' in request.data:
            user.langue = request.data['langue']
        user.save()

        if 'numero_permis' in request.data:
            camioneur.numero_permis = request.data['numero_permis']
            camioneur.save()

        return Response({'message': 'Profil mis à jour.'})


class AdminCamioneurPositionsView(generics.ListAPIView):
    """Admin — voir la position actuelle de tous les camioneurs disponibles."""
    permission_classes = [IsAdminRole]

    @extend_schema(tags=['Admin'], summary='Positions GPS de tous les camioneurs')
    def get(self, request):
        camioneurs = Camioneur.objects.filter(
            statut_inscription='accepte',
            latitude_actuelle__isnull=False,
        ).select_related('user')

        data = [
            {
                'id': c.id,
                'nom': c.user.nom,
                'email': c.user.email,
                'disponible': c.disponible,
                'latitude': str(c.latitude_actuelle),
                'longitude': str(c.longitude_actuelle),
            }
            for c in camioneurs
        ]
        return Response({'count': len(data), 'camioneurs': data})
