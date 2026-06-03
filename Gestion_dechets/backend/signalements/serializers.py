"""
Serializers — signalements
"""
from rest_framework import serializers
from .models import Signalement


class SignalementSerializer(serializers.ModelSerializer):
    citoyen_nom = serializers.CharField(source='citoyen.user.nom', read_only=True)
    camioneur_nom = serializers.SerializerMethodField()
    distance_km = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Signalement
        fields = [
            'id', 'citoyen', 'citoyen_nom',
            'photo', 'latitude', 'longitude',
            'description', 'type_dechet', 'statut',
            'camioneur_assigne', 'camioneur_nom',
            'date_signalement', 'date_modification',
            'distance_km',
        ]
        read_only_fields = [
            'id', 'citoyen', 'statut',
            'camioneur_assigne', 'date_signalement', 'date_modification',
        ]

    def get_camioneur_nom(self, obj):
        if obj.camioneur_assigne:
            return obj.camioneur_assigne.user.nom
        return None


class SignalementCreateSerializer(serializers.ModelSerializer):
    """Utilisé par le citoyen pour créer un signalement depuis le mobile."""

    class Meta:
        model = Signalement
        fields = ['id', 'photo', 'latitude', 'longitude', 'description', 'type_dechet', 'statut']
        read_only_fields = ['id', 'statut']

    def validate_latitude(self, value):
        if not (-90 <= float(value) <= 90):
            raise serializers.ValidationError('Latitude invalide (doit être entre -90 et 90).')
        return value

    def validate_longitude(self, value):
        if not (-180 <= float(value) <= 180):
            raise serializers.ValidationError('Longitude invalide (doit être entre -180 et 180).')
        return value

    def create(self, validated_data):
        citoyen = self.context['request'].user.profil_citoyen
        return Signalement.objects.create(citoyen=citoyen, **validated_data)


class SignalementProximiteSerializer(serializers.ModelSerializer):
    """Signalement avec distance — pour le camioneur mobile."""
    distance_km = serializers.FloatField(read_only=True)
    citoyen_nom = serializers.CharField(source='citoyen.user.nom', read_only=True)

    class Meta:
        model = Signalement
        fields = [
            'id', 'citoyen_nom',
            'photo', 'latitude', 'longitude',
            'description', 'type_dechet', 'statut',
            'date_signalement', 'distance_km',
        ]
