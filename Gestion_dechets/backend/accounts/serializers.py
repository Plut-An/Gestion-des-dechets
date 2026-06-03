"""
Serializers — accounts
"""
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser, Citoyen, Camioneur


# ---------------------------------------------------------------------------
# JWT personnalisé — ajouter role + nom dans le token
# ---------------------------------------------------------------------------
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['nom'] = user.nom
        token['role'] = user.role
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'nom': self.user.nom,
            'email': self.user.email,
            'role': self.user.role,
            'langue': self.user.langue,
        }
        return data


# ---------------------------------------------------------------------------
# Profil Citoyen
# ---------------------------------------------------------------------------
class CitoyenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citoyen
        fields = ['solde_eco_points', 'photo_profil', 'adresse', 'statut_inscription']
        read_only_fields = ['solde_eco_points', 'statut_inscription']


class CitoyenDetailSerializer(serializers.ModelSerializer):
    """Citoyen avec infos user imbriquées — pour l'admin."""
    email = serializers.EmailField(source='user.email', read_only=True)
    nom = serializers.CharField(source='user.nom', read_only=True)
    langue = serializers.CharField(source='user.langue', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    date_creation = serializers.DateTimeField(source='user.date_creation', read_only=True)

    class Meta:
        model = Citoyen
        fields = [
            'id', 'email', 'nom', 'langue', 'is_active', 'date_creation',
            'solde_eco_points', 'photo_profil', 'adresse', 'statut_inscription',
        ]


# ---------------------------------------------------------------------------
# Profil Camioneur
# ---------------------------------------------------------------------------
class CamioneurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camioneur
        fields = [
            'numero_permis', 'disponible',
            'latitude_actuelle', 'longitude_actuelle',
            'statut_inscription', 'mot_de_passe_temporaire', 'solde_eco_points',
        ]
        read_only_fields = ['statut_inscription', 'mot_de_passe_temporaire', 'solde_eco_points']


class CamioneurDetailSerializer(serializers.ModelSerializer):
    """Camioneur avec infos user imbriquées — pour l'admin."""
    email = serializers.EmailField(source='user.email', read_only=True)
    nom = serializers.CharField(source='user.nom', read_only=True)
    langue = serializers.CharField(source='user.langue', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    date_creation = serializers.DateTimeField(source='user.date_creation', read_only=True)

    class Meta:
        model = Camioneur
        fields = [
            'id', 'email', 'nom', 'langue', 'is_active', 'date_creation',
            'numero_permis', 'disponible',
            'latitude_actuelle', 'longitude_actuelle',
            'statut_inscription', 'mot_de_passe_temporaire', 'solde_eco_points',
        ]


# ---------------------------------------------------------------------------
# Inscription Citoyen (mobile)
# ---------------------------------------------------------------------------
class RegisterCitoyenSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label='Confirmation mot de passe')
    adresse = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'nom', 'langue', 'password', 'password2', 'adresse']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password': 'Les mots de passe ne correspondent pas.'})
        return attrs

    def create(self, validated_data):
        adresse = validated_data.pop('adresse', '')
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            nom=validated_data['nom'],
            langue=validated_data.get('langue', 'FR'),
            password=validated_data['password'],
            role='citoyen',
            is_active=True,
        )
        Citoyen.objects.create(user=user, adresse=adresse)
        return user


# ---------------------------------------------------------------------------
# Inscription Camioneur (mobile)
# ---------------------------------------------------------------------------
class RegisterCamioneurSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label='Confirmation mot de passe')
    numero_permis = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'nom', 'langue', 'password', 'password2', 'numero_permis']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password': 'Les mots de passe ne correspondent pas.'})
        return attrs

    def create(self, validated_data):
        numero_permis = validated_data.pop('numero_permis')
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            nom=validated_data['nom'],
            langue=validated_data.get('langue', 'FR'),
            password=validated_data['password'],
            role='camioneur',
            is_active=True,
        )
        Camioneur.objects.create(user=user, numero_permis=numero_permis)
        return user


# ---------------------------------------------------------------------------
# Changement de mot de passe
# ---------------------------------------------------------------------------
class ChangePasswordSerializer(serializers.Serializer):
    ancien_mot_de_passe = serializers.CharField(required=True)
    nouveau_mot_de_passe = serializers.CharField(required=True, validators=[validate_password])
    confirmation = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['nouveau_mot_de_passe'] != attrs['confirmation']:
            raise serializers.ValidationError({'confirmation': 'Les mots de passe ne correspondent pas.'})
        return attrs


# ---------------------------------------------------------------------------
# Profil courant (GET /api/auth/me/)
# ---------------------------------------------------------------------------
class MeSerializer(serializers.ModelSerializer):
    profil_citoyen = CitoyenSerializer(read_only=True)
    profil_camioneur = CamioneurSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'nom', 'role', 'langue',
            'is_active', 'date_creation',
            'profil_citoyen', 'profil_camioneur',
        ]
        read_only_fields = ['id', 'role', 'date_creation']


# ---------------------------------------------------------------------------
# Admin — Création d'un utilisateur
# ---------------------------------------------------------------------------
class AdminCreateUserSerializer(serializers.ModelSerializer):
    """Utilisé par l'admin pour créer citoyens ou camioneurs."""
    password = serializers.CharField(write_only=True, default='ChangeMe123!')
    numero_permis = serializers.CharField(write_only=True, required=False, allow_blank=True)
    adresse = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'nom', 'role', 'langue', 'password', 'numero_permis', 'adresse']

    def validate(self, attrs):
        role = attrs.get('role')
        if role == 'camioneur' and not attrs.get('numero_permis'):
            raise serializers.ValidationError({'numero_permis': 'Le numéro de permis est obligatoire pour un camioneur.'})
        return attrs

    def create(self, validated_data):
        numero_permis = validated_data.pop('numero_permis', '')
        adresse = validated_data.pop('adresse', '')
        role = validated_data.get('role', 'citoyen')

        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            nom=validated_data['nom'],
            role=role,
            langue=validated_data.get('langue', 'FR'),
            password=validated_data.get('password', 'ChangeMe123!'),
            is_active=True,
        )
        if role == 'citoyen':
            Citoyen.objects.create(user=user, adresse=adresse)
        elif role == 'camioneur':
            Camioneur.objects.create(
                user=user,
                numero_permis=numero_permis,
                mot_de_passe_temporaire=True,
            )
        return user


# ---------------------------------------------------------------------------
# Mise à jour position GPS (camioneur)
# ---------------------------------------------------------------------------
class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camioneur
        fields = ['latitude_actuelle', 'longitude_actuelle', 'disponible']
