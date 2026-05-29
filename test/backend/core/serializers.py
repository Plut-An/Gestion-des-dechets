"""
Sérialiseurs DRF — API « Gestion des déchets » (cahier des charges ESMIA).

Couverture fonctionnelle :
  - Scénario 1 : inscription citoyen + justificatifs (Must — Gestion des inscriptions).
  - Scénario 2 : signalement citoyen + refus chauffeur (Must — Signalement / Contrôle collecte).
  - Scénario 3 & Réseau social éco : événements, likes, commentaires (Must — Module événements).
"""
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from rest_framework import serializers

from .models import (
    Chauffeur,
    Citoyen,
    Commentaire,
    EvenementEcologique,
    InteractionLike,
    RefusCollecte,
    RoleUtilisateur,
    Signalement,
    Utilisateur,
)


# ---------------------------------------------------------------------------
# Utilisateurs — authentification & profils
# ---------------------------------------------------------------------------


class UtilisateurSerializer(serializers.ModelSerializer):
    """
    Sérialiseur générique (affichage des informations de base).
    Cahier des charges : Authentification & profils — rôle et identité.
    """

    class Meta:
        model = Utilisateur
        fields = ["id", "username", "email", "role"]
        read_only_fields = fields


class CitoyenSerializer(serializers.ModelSerializer):
    """Profil citoyen détaillé (consultation après connexion)."""

    statut_compte = serializers.SerializerMethodField()

    class Meta:
        model = Citoyen
        fields = [
            "id",
            "username",
            "email",
            "nom_utilisateur",
            "role",
            "is_active",
            "solde_eco_points",
            "statut_compte",
        ]
        read_only_fields = fields

    def get_statut_compte(self, obj: Citoyen) -> str:
        return "actif" if obj.is_active else "en_attente_validation"


class ChauffeurSerializer(serializers.ModelSerializer):
    """Profil chauffeur détaillé."""

    class Meta:
        model = Chauffeur
        fields = [
            "id",
            "username",
            "email",
            "role",
            "numero_permis",
            "disponibilite",
        ]
        read_only_fields = fields


class ProfilModificationSerializer(serializers.Serializer):
    """Champs modifiables via modifierProfil() du diagramme de classes."""

    email = serializers.EmailField(required=False)
    nom_utilisateur = serializers.CharField(max_length=150, required=False)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_email(self, value: str) -> str:
        validate_email(value)
        utilisateur = self.context["request"].user
        if Utilisateur.objects.filter(email__iexact=value).exclude(pk=utilisateur.pk).exists():
            raise serializers.ValidationError("Cette adresse e-mail est déjà utilisée.")
        return value.lower()


class CitoyenInscriptionSerializer(serializers.ModelSerializer):
    """
    Scénario 1 — Inscription soumise à validation administrateur.

    Le visiteur télécharge pièce d'identité et certificat de résidence ;
    le compte est créé avec is_active=False jusqu'à validation (Must).
    """

    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = Citoyen
        fields = [
            "username",
            "email",
            "password",
            "piece_identite",
            "certificat_residence",
        ]

    def validate_email(self, value: str) -> str:
        validate_email(value)
        if Utilisateur.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Cette adresse e-mail est déjà utilisée.")
        return value.lower()

    def validate_username(self, value: str) -> str:
        if Utilisateur.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return value

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def create(self, validated_data: dict) -> Citoyen:
        password = validated_data.pop("password")

        citoyen = Citoyen(
            **validated_data,
            role=RoleUtilisateur.CITOYEN,
            is_active=False,
        )
        citoyen.set_password(password)
        citoyen.save()
        citoyen.creer_compte()
        return citoyen


class CitoyenEnAttenteSerializer(serializers.ModelSerializer):
    """
    Scénario 1 — Liste des inscriptions en attente (dashboard administrateur).

    Expose nom, adresse (dérivée du profil), e-mail et URLs des justificatifs.
    """

    nom = serializers.SerializerMethodField()
    adresse = serializers.SerializerMethodField()
    piece_identite_url = serializers.SerializerMethodField()
    certificat_residence_url = serializers.SerializerMethodField()

    class Meta:
        model = Citoyen
        fields = [
            "id",
            "nom",
            "adresse",
            "email",
            "piece_identite_url",
            "certificat_residence_url",
            "date_inscription",
        ]

    def get_nom(self, obj: Citoyen) -> str:
        if obj.nom_utilisateur:
            return obj.nom_utilisateur
        nom_complet = obj.get_full_name().strip()
        return nom_complet or obj.username

    def get_adresse(self, obj: Citoyen) -> str:
        nom_complet = obj.get_full_name().strip()
        if nom_complet:
            return nom_complet
        return "Non renseignée"

    def _url_fichier(self, obj: Citoyen, champ: str) -> str | None:
        fichier = getattr(obj, champ, None)
        if not fichier:
            return None
        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_uri(fichier.url)
        return fichier.url

    def get_piece_identite_url(self, obj: Citoyen) -> str | None:
        return self._url_fichier(obj, "piece_identite")

    def get_certificat_residence_url(self, obj: Citoyen) -> str | None:
        return self._url_fichier(obj, "certificat_residence")


# ---------------------------------------------------------------------------
# Scénario 2 — Signalement citoyen & refus chauffeur
# ---------------------------------------------------------------------------


class SignalementSerializer(serializers.ModelSerializer):
    """
    Must — Signalement citoyen : photo, géolocalisation, type de déchet.

    Le citoyen est renseigné automatiquement côté vue (utilisateur connecté).
    """

    citoyen = UtilisateurSerializer(read_only=True)

    class Meta:
        model = Signalement
        fields = [
            "id",
            "citoyen",
            "photo",
            "latitude",
            "longitude",
            "type_dechet",
            "statut",
            "date_creation",
        ]
        read_only_fields = ["id", "citoyen", "statut", "date_creation"]


class RefusCollecteSerializer(serializers.ModelSerializer):
    """
    Scénario 2 (variante refus) — Justification obligatoire du chauffeur.

    Could/Must — Contrôle collecte : motif écrit + photo justificative horodatée.
    """

    chauffeur = UtilisateurSerializer(read_only=True)

    class Meta:
        model = RefusCollecte
        fields = [
            "id",
            "chauffeur",
            "signalement",
            "motif_ecrit",
            "photo_justificative",
            "date_refus",
        ]
        read_only_fields = ["id", "chauffeur", "date_refus"]


# ---------------------------------------------------------------------------
# Réseau social éco — événements, commentaires, likes
# ---------------------------------------------------------------------------


class CommentaireSerializer(serializers.ModelSerializer):
    """Commentaire sur un événement (Module événements & social — Must)."""

    auteur = UtilisateurSerializer(read_only=True)

    class Meta:
        model = Commentaire
        fields = ["id", "evenement", "auteur", "texte", "date_publication"]
        read_only_fields = ["id", "evenement", "auteur", "date_publication"]


class InteractionLikeSerializer(serializers.ModelSerializer):
    """Like unique par citoyen et par événement (contrainte métier du modèle)."""

    citoyen = UtilisateurSerializer(read_only=True)

    class Meta:
        model = InteractionLike
        fields = ["id", "evenement", "citoyen", "date_like"]
        read_only_fields = ["id", "evenement", "citoyen", "date_like"]


class EvenementEcologiqueSerializer(serializers.ModelSerializer):
    """
    Scénario 3 — Événement écologique avec fil social imbriqué.

    Inclut les commentaires et likes associés (Must — Module événements & social).
    """

    commentaires = CommentaireSerializer(many=True, read_only=True)
    likes = InteractionLikeSerializer(many=True, read_only=True)
    nombre_likes = serializers.SerializerMethodField()
    nombre_commentaires = serializers.SerializerMethodField()

    class Meta:
        model = EvenementEcologique
        fields = [
            "id",
            "titre",
            "description",
            "date_evenement",
            "lieu",
            "compteur_volontaires",
            "date_creation",
            "commentaires",
            "likes",
            "nombre_likes",
            "nombre_commentaires",
        ]
        read_only_fields = [
            "id",
            "compteur_volontaires",
            "date_creation",
            "commentaires",
            "likes",
            "nombre_likes",
            "nombre_commentaires",
        ]

    def get_nombre_likes(self, obj: EvenementEcologique) -> int:
        return obj.likes.count()

    def get_nombre_commentaires(self, obj: EvenementEcologique) -> int:
        return obj.commentaires.count()


class CommentaireCreationSerializer(serializers.ModelSerializer):
    """Écriture d'un commentaire (texte seul — auteur et événement injectés en vue)."""

    class Meta:
        model = Commentaire
        fields = ["texte"]


class ParticipationEvenementSerializer(serializers.Serializer):
    """Corps vide : la participation est déclenchée par l'action POST."""

    pass
