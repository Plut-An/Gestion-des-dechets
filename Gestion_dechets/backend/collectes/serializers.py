"""
Serializers — collectes
"""
from rest_framework import serializers
from accounts.serializers import CamioneurSerializer
from .models import PositionCamioneur


class PositionCamioneurSerializer(serializers.ModelSerializer):
    class Meta:
        model = PositionCamioneur
        fields = ['id', 'latitude', 'longitude', 'horodatage']
        read_only_fields = ['id', 'horodatage']


class MettreAJourPositionSerializer(serializers.Serializer):
    """Payload pour mettre à jour la position GPS du camioneur."""
    latitude = serializers.DecimalField(max_digits=10, decimal_places=8)
    longitude = serializers.DecimalField(max_digits=11, decimal_places=8)
    disponible = serializers.BooleanField(required=False)

    def validate_latitude(self, value):
        if not (-90 <= float(value) <= 90):
            raise serializers.ValidationError('Latitude invalide.')
        return value

    def validate_longitude(self, value):
        if not (-180 <= float(value) <= 180):
            raise serializers.ValidationError('Longitude invalide.')
        return value
