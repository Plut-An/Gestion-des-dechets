"""
Views Admin — CRUD complet citoyens, camioneurs, associations
"""
from django.db.models import Q, Sum
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from accounts.models import CustomUser, Citoyen, Camioneur
from accounts.permissions import IsAdminRole
from accounts.serializers import (
    AdminCreateUserSerializer,
    CitoyenDetailSerializer,
    CamioneurDetailSerializer,
    MeSerializer,
)


# ---------------------------------------------------------------------------
# Dashboard global
# ---------------------------------------------------------------------------
class DashboardView(APIView):
    permission_classes = [IsAdminRole]

    @extend_schema(tags=['Admin'], summary='Tableau de bord statistiques')
    def get(self, request):
        from signalements.models import Signalement
        from associations.models import Association, Adhesion

        data = {
            'total_citoyens': Citoyen.objects.count(),
            'citoyens_en_attente': Citoyen.objects.filter(statut_inscription='en_attente').count(),
            'citoyens_acceptes': Citoyen.objects.filter(statut_inscription='accepte').count(),
            'total_camioneurs': Camioneur.objects.count(),
            'camioneurs_en_attente': Camioneur.objects.filter(statut_inscription='en_attente').count(),
            'camioneurs_acceptes': Camioneur.objects.filter(statut_inscription='accepte').count(),
            'camioneurs_disponibles': Camioneur.objects.filter(disponible=True, statut_inscription='accepte').count(),
            'total_associations': Association.objects.count(),
            'total_signalements': Signalement.objects.count(),
            'signalements_en_attente': Signalement.objects.filter(statut='signale').count(),
            'signalements_traites': Signalement.objects.filter(statut='traite').count(),
            'signalements_en_cours': Signalement.objects.filter(
                statut__in=['assigne', 'en_cours']
            ).count(),
            'total_eco_points': Citoyen.objects.aggregate(
                total=Sum('solde_eco_points')
            )['total'] or 0,
        }
        return Response(data)


# ---------------------------------------------------------------------------
# CRUD Citoyens
# ---------------------------------------------------------------------------
class CitoyenListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdminCreateUserSerializer
        return CitoyenDetailSerializer

    def get_queryset(self):
        qs = Citoyen.objects.select_related('user').order_by('-date_modification')
        statut = self.request.query_params.get('statut')
        if statut:
            qs = qs.filter(statut_inscription=statut)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(user__nom__icontains=search) | Q(user__email__icontains=search)
            )
        return qs

    @extend_schema(tags=['Admin'], summary='Liste des citoyens')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=['Admin'], summary='Créer un citoyen')
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data['role'] = 'citoyen'
        serializer = AdminCreateUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'message': f'Citoyen {user.nom} créé avec succès.', 'id': user.id},
            status=status.HTTP_201_CREATED
        )


class CitoyenDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = CitoyenDetailSerializer
    queryset = Citoyen.objects.select_related('user').all()

    @extend_schema(tags=['Admin'], summary='Détail citoyen')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=['Admin'], summary='Modifier citoyen')
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(tags=['Admin'], summary='Supprimer citoyen')
    def delete(self, request, *args, **kwargs):
        citoyen = self.get_object()
        user = citoyen.user
        user.delete()  # cascade supprime le profil citoyen
        return Response({'message': 'Citoyen supprimé.'}, status=status.HTTP_204_NO_CONTENT)


class ValiderCitoyenView(APIView):
    """Valider ou refuser l'inscription d'un citoyen."""
    permission_classes = [IsAdminRole]

    @extend_schema(tags=['Admin'], summary='Valider/Refuser inscription citoyen')
    def post(self, request, pk):
        try:
            citoyen = Citoyen.objects.get(pk=pk)
        except Citoyen.DoesNotExist:
            return Response({'error': 'Citoyen introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')  # 'accepter' ou 'refuser'
        if action == 'accepter':
            citoyen.statut_inscription = 'accepte'
            citoyen.save()
            return Response({'message': f'Inscription de {citoyen.user.nom} acceptée.'})
        elif action == 'refuser':
            citoyen.statut_inscription = 'refuse'
            citoyen.save()
            return Response({'message': f'Inscription de {citoyen.user.nom} refusée.'})
        else:
            return Response(
                {'error': 'Action invalide. Utilisez "accepter" ou "refuser".'},
                status=status.HTTP_400_BAD_REQUEST
            )


# ---------------------------------------------------------------------------
# CRUD Camioneurs
# ---------------------------------------------------------------------------
class CamioneurListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdminCreateUserSerializer
        return CamioneurDetailSerializer

    def get_queryset(self):
        qs = Camioneur.objects.select_related('user').order_by('-date_modification')
        statut = self.request.query_params.get('statut')
        if statut:
            qs = qs.filter(statut_inscription=statut)
        disponible = self.request.query_params.get('disponible')
        if disponible is not None:
            qs = qs.filter(disponible=disponible.lower() == 'true')
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(user__nom__icontains=search) |
                Q(user__email__icontains=search) |
                Q(numero_permis__icontains=search)
            )
        return qs

    @extend_schema(tags=['Admin'], summary='Liste des camioneurs')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=['Admin'], summary='Créer un camioneur')
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data['role'] = 'camioneur'
        serializer = AdminCreateUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'message': f'Camioneur {user.nom} créé. Un mot de passe temporaire a été assigné.', 'id': user.id},
            status=status.HTTP_201_CREATED
        )


class CamioneurDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = CamioneurDetailSerializer
    queryset = Camioneur.objects.select_related('user').all()

    @extend_schema(tags=['Admin'], summary='Détail camioneur')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=['Admin'], summary='Modifier camioneur')
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(tags=['Admin'], summary='Supprimer camioneur')
    def delete(self, request, *args, **kwargs):
        camioneur = self.get_object()
        camioneur.user.delete()
        return Response({'message': 'Camioneur supprimé.'}, status=status.HTTP_204_NO_CONTENT)


class ValiderCamioneurView(APIView):
    """Valider ou refuser l'inscription d'un camioneur."""
    permission_classes = [IsAdminRole]

    @extend_schema(tags=['Admin'], summary='Valider/Refuser inscription camioneur')
    def post(self, request, pk):
        try:
            camioneur = Camioneur.objects.get(pk=pk)
        except Camioneur.DoesNotExist:
            return Response({'error': 'Camioneur introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        if action == 'accepter':
            camioneur.statut_inscription = 'accepte'
            camioneur.save()
            return Response({'message': f'Inscription de {camioneur.user.nom} acceptée.'})
        elif action == 'refuser':
            camioneur.statut_inscription = 'refuse'
            camioneur.save()
            return Response({'message': f'Inscription de {camioneur.user.nom} refusée.'})
        else:
            return Response(
                {'error': 'Action invalide. Utilisez "accepter" ou "refuser".'},
                status=status.HTTP_400_BAD_REQUEST
            )
