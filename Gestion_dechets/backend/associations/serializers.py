"""
Serializers — associations
"""
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from .models import Association, Adhesion, AcceptationCamioneur
from accounts.models import Citoyen, Camioneur


class AssociationSerializer(serializers.ModelSerializer):
    nb_membres = serializers.SerializerMethodField()
    nb_camioneurs = serializers.SerializerMethodField()

    class Meta:
        model = Association
        fields = [
            'id', 'nom', 'description', 'ville', 'logo',
            'date_inscription', 'nb_membres', 'nb_camioneurs',
        ]
        read_only_fields = ['id', 'date_inscription']

    def get_nb_membres(self, obj):
        return obj.adhesions.filter(statut='accepte').count()

    def get_nb_camioneurs(self, obj):
        return obj.camioneurs_lies.filter(statut='accepte').count()


class AssociationDetailSerializer(AssociationSerializer):
    """Version étendue avec infos du compte de connexion."""
    email = serializers.EmailField(source='user.email', read_only=True, default=None)

    class Meta(AssociationSerializer.Meta):
        fields = AssociationSerializer.Meta.fields + ['email']


class AssociationCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, validators=[validate_password], style={'input_type': 'password'})

    class Meta:
        model = Association
        fields = ['id', 'nom', 'description', 'ville', 'logo', 'email', 'password']
        read_only_fields = ['id']

    def validate_email(self, value):
        from accounts.models import CustomUser
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Cette adresse e-mail est déjà utilisée.')
        return value

    def create(self, validated_data):
        from accounts.models import CustomUser
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        with transaction.atomic():
            user = CustomUser.objects.create_user(
                email=email,
                nom=validated_data.get('nom'),
                password=password,
                role='association',
                is_active=True,
            )
            association = Association.objects.create(user=user, **validated_data)
        return association


class AdhesionSerializer(serializers.ModelSerializer):
    citoyen_nom = serializers.CharField(source='citoyen.user.nom', read_only=True)
    citoyen_email = serializers.EmailField(source='citoyen.user.email', read_only=True)
    citoyen_eco_points = serializers.IntegerField(source='citoyen.solde_eco_points', read_only=True)
    association_nom = serializers.CharField(source='association.nom', read_only=True)

    class Meta:
        model = Adhesion
        fields = [
            'id', 'citoyen', 'citoyen_nom', 'citoyen_email', 'citoyen_eco_points',
            'association', 'association_nom',
            'statut', 'date_demande', 'motif_refus',
        ]
        read_only_fields = ['id', 'statut', 'date_demande']


class AdhesionCreateSerializer(serializers.ModelSerializer):
    """Utilisé quand un citoyen fait une demande d'adhésion."""
    class Meta:
        model = Adhesion
        fields = ['association']

    def validate(self, attrs):
        request = self.context['request']
        try:
            citoyen = request.user.profil_citoyen
        except Exception:
            raise serializers.ValidationError("Seuls les citoyens peuvent faire une demande d'adhésion.")

        association = attrs['association']
        if Adhesion.objects.filter(citoyen=citoyen, association=association).exists():
            raise serializers.ValidationError("Vous avez déjà fait une demande pour cette association.")
        return attrs

    def create(self, validated_data):
        citoyen = self.context['request'].user.profil_citoyen
        return Adhesion.objects.create(citoyen=citoyen, **validated_data)


class AcceptationCamioneurSerializer(serializers.ModelSerializer):
    camioneur_nom = serializers.CharField(source='camioneur.user.nom', read_only=True)
    camioneur_email = serializers.EmailField(source='camioneur.user.email', read_only=True)
    camioneur_permis = serializers.CharField(source='camioneur.numero_permis', read_only=True)
    association_nom = serializers.CharField(source='association.nom', read_only=True)

    class Meta:
        model = AcceptationCamioneur
        fields = [
            'id', 'camioneur', 'camioneur_nom', 'camioneur_email', 'camioneur_permis',
            'association', 'association_nom',
            'statut', 'date_demande',
        ]
        read_only_fields = ['id', 'statut', 'date_demande']
