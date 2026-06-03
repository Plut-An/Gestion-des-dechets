"""
Serializers — evenements
"""
from rest_framework import serializers
from .models import Annonce, EvenementEcologique, Participation


class AnnonceSerializer(serializers.ModelSerializer):
    association_nom = serializers.CharField(source='association.nom', read_only=True)

    class Meta:
        model = Annonce
        fields = [
            'id', 'association', 'association_nom',
            'titre', 'contenu', 'image', 'type', 'date_publication',
        ]
        read_only_fields = ['id', 'association', 'date_publication']


class EvenementSerializer(serializers.ModelSerializer):
    association_nom = serializers.CharField(source='association.nom', read_only=True)
    compteur_volontaires = serializers.IntegerField(read_only=True)
    compteur_presents = serializers.IntegerField(read_only=True)
    je_participe = serializers.SerializerMethodField()

    class Meta:
        model = EvenementEcologique
        fields = [
            'id', 'association', 'association_nom',
            'titre', 'description', 'date_evenement',
            'lieu', 'latitude', 'longitude',
            'statut', 'date_creation',
            'compteur_volontaires', 'compteur_presents',
            'je_participe',
        ]
        read_only_fields = ['id', 'association', 'date_creation']

    def get_je_participe(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        if not hasattr(request.user, 'profil_citoyen'):
            return False
        return obj.participations.filter(citoyen=request.user.profil_citoyen).exists()


class ParticipationSerializer(serializers.ModelSerializer):
    citoyen_nom = serializers.CharField(source='citoyen.user.nom', read_only=True)
    citoyen_email = serializers.EmailField(source='citoyen.user.email', read_only=True)
    evenement_titre = serializers.CharField(source='evenement.titre', read_only=True)

    class Meta:
        model = Participation
        fields = [
            'id', 'citoyen', 'citoyen_nom', 'citoyen_email',
            'evenement', 'evenement_titre',
            'date_participation', 'presence_confirmee',
        ]
        read_only_fields = ['id', 'date_participation', 'presence_confirmee']


class CommentaireSerializer(serializers.ModelSerializer):
    auteur_nom = serializers.CharField(source='auteur.nom', read_only=True)

    class Meta:
        from .models import Commentaire
        model = Commentaire
        fields = ['id', 'evenement', 'auteur', 'auteur_nom', 'contenu', 'date_publication']
        read_only_fields = ['id', 'evenement', 'auteur', 'date_publication']
