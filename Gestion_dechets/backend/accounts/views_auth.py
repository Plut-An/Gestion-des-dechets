"""
Views — Auth (register, login, logout, me, change-password)
"""
from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema, OpenApiResponse

from accounts.models import CustomUser, Camioneur
from accounts.serializers import (
    CustomTokenObtainPairSerializer,
    RegisterCitoyenSerializer,
    RegisterCamioneurSerializer,
    ChangePasswordSerializer,
    MeSerializer,
)


class LoginView(TokenObtainPairView):
    """
    Connexion — retourne access + refresh tokens JWT avec les infos utilisateur.
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    @extend_schema(tags=['Auth'], summary='Connexion utilisateur')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RegisterCitoyenView(generics.CreateAPIView):
    """
    Inscription d'un nouveau citoyen (mobile).
    Le compte est créé actif avec statut 'en_attente' en attente de validation admin.
    """
    serializer_class = RegisterCitoyenSerializer
    permission_classes = [AllowAny]

    @extend_schema(tags=['Auth'], summary='Inscription citoyen (mobile)')
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Générer tokens JWT directement
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Inscription réussie. Votre compte est en attente de validation.',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'nom': user.nom,
                'email': user.email,
                'role': user.role,
            }
        }, status=status.HTTP_201_CREATED)


class RegisterCamioneurView(generics.CreateAPIView):
    """
    Inscription d'un nouveau camioneur (mobile).
    """
    serializer_class = RegisterCamioneurSerializer
    permission_classes = [AllowAny]

    @extend_schema(tags=['Auth'], summary='Inscription camioneur (mobile)')
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Inscription réussie. Votre compte est en attente de validation par l\'administrateur.',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'nom': user.nom,
                'email': user.email,
                'role': user.role,
            }
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """
    Déconnexion — invalide le refresh token (blacklist).
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Auth'], summary='Déconnexion')
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Le refresh token est requis.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Déconnexion réussie.'}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({'error': 'Token invalide.'}, status=status.HTTP_400_BAD_REQUEST)


class MeView(generics.RetrieveUpdateAPIView):
    """
    Profil de l'utilisateur connecté.
    GET: récupère le profil
    PUT/PATCH: met à jour nom et langue
    """
    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Auth'], summary='Mon profil')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """
    Changement de mot de passe — obligatoire pour les camioneurs avec mot de passe temporaire.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Auth'], summary='Changer le mot de passe')
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['ancien_mot_de_passe']):
            return Response(
                {'ancien_mot_de_passe': 'Mot de passe incorrect.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['nouveau_mot_de_passe'])
        user.save()

        # Marquer le mot de passe temporaire comme changé (camioneur)
        if hasattr(user, 'profil_camioneur'):
            user.profil_camioneur.mot_de_passe_temporaire = False
            user.profil_camioneur.save()

        return Response({'message': 'Mot de passe changé avec succès.'}, status=status.HTTP_200_OK)
