"""
Vues API REST — plateforme « Gestion des déchets » (cahier des charges ESMIA).

Endpoints alignés sur :
  - Must : authentification, inscription, signalements, réseau social éco, dashboard admin.
  - Exigences algorithmiques : comparaison Baseline vs Dijkstra (services.py).
"""
from rest_framework import status, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    CentreDeTri,
    Chauffeur,
    Citoyen,
    Commentaire,
    EvenementEcologique,
    InteractionLike,
    RoleUtilisateur,
    Signalement,
    Utilisateur,
)
from .permissions import IsAdministrateur, IsChauffeur, IsCitoyen
from .serializers import (
    ChauffeurSerializer,
    CitoyenEnAttenteSerializer,
    CitoyenInscriptionSerializer,
    CitoyenSerializer,
    CommentaireCreationSerializer,
    CommentaireSerializer,
    EvenementEcologiqueSerializer,
    InteractionLikeSerializer,
    ProfilModificationSerializer,
    RefusCollecteSerializer,
    SignalementSerializer,
    UtilisateurSerializer,
)
from .services import simuler_comparaison_algorithmes


# ---------------------------------------------------------------------------
# Utilitaires profil
# ---------------------------------------------------------------------------


def _get_profil_utilisateur(utilisateur: Utilisateur) -> Utilisateur:
    citoyen = Citoyen.objects.filter(pk=utilisateur.pk).first()
    if citoyen is not None:
        return citoyen
    chauffeur = Chauffeur.objects.filter(pk=utilisateur.pk).first()
    if chauffeur is not None:
        return chauffeur
    return utilisateur


def _get_serializer_pour_profil(utilisateur: Utilisateur):
    if isinstance(utilisateur, Citoyen):
        return CitoyenSerializer(utilisateur)
    if isinstance(utilisateur, Chauffeur):
        return ChauffeurSerializer(utilisateur)
    return UtilisateurSerializer(utilisateur)


def _get_citoyen(utilisateur: Utilisateur) -> Citoyen | None:
    return Citoyen.objects.filter(pk=utilisateur.pk, is_active=True).first()


def _get_chauffeur(utilisateur: Utilisateur) -> Chauffeur | None:
    return Chauffeur.objects.filter(pk=utilisateur.pk, is_active=True).first()


# ---------------------------------------------------------------------------
# Authentification — seConnecter() / inscription Scénario 1
# ---------------------------------------------------------------------------


class ConnexionView(ObtainAuthToken):
    """
    Must — Authentification : implémentation de seConnecter() via token DRF.

    POST { "username": "...", "password": "..." } → { "token": "..." }
    """

    permission_classes = [AllowAny]


class CitoyenInscriptionView(CreateAPIView):
    """
    Scénario 1 — Inscription citoyen avec justificatifs (multipart/form-data).

    Must — Gestion des inscriptions : statut « en attente » jusqu'à validation admin.
    MultiPartParser requis pour piece_identite et certificat_residence.
    """

    serializer_class = CitoyenInscriptionSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        citoyen = serializer.save()
        return Response(
            {
                "message": (
                    "Inscription enregistrée (Scénario 1). Votre compte est en attente "
                    "de validation par un administrateur avant toute connexion."
                ),
                "utilisateur": CitoyenSerializer(citoyen).data,
            },
            status=status.HTTP_201_CREATED,
        )


class ProfilViewSet(viewsets.ViewSet):
    """Must — Authentification & profils : consulter / modifierProfil()."""

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get", "patch", "put"], url_path="me")
    def me(self, request):
        utilisateur = request.user
        profil = _get_profil_utilisateur(utilisateur)

        if request.method == "GET":
            return Response(_get_serializer_pour_profil(profil).data)

        serializer = ProfilModificationSerializer(
            data=request.data,
            partial=request.method == "PATCH",
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        utilisateur.modifier_profil(**serializer.validated_data)
        profil = _get_profil_utilisateur(utilisateur)
        return Response(_get_serializer_pour_profil(profil).data)


# ---------------------------------------------------------------------------
# Dashboard admin — optimisation de tournée (Dijkstra vs Baseline)
# ---------------------------------------------------------------------------


class OptimisationTourneeView(APIView):
    """
    Must — Dashboard administrateur : métriques d'optimisation des tournées.

    Appelle simuler_comparaison_algorithmes() (tas binaire + Dijkstra + glouton
    vs baseline) pour alimenter le rapport JSON du tableau de bord.
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def _extraire_centre_tri_id(self, request) -> int | None:
        valeur = request.query_params.get("centre_tri_id") or request.data.get(
            "centre_tri_id"
        )
        if valeur is None:
            return None
        try:
            return int(valeur)
        except (TypeError, ValueError):
            return None

    def post(self, request):
        return self._executer_optimisation(request)

    def get(self, request):
        return self._executer_optimisation(request)

    def _executer_optimisation(self, request):
        centre_tri_id = self._extraire_centre_tri_id(request)
        if centre_tri_id is None:
            return Response(
                {
                    "erreur": (
                        "Paramètre obligatoire « centre_tri_id » "
                        "(query string ou corps JSON)."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not CentreDeTri.objects.filter(pk=centre_tri_id).exists():
            return Response(
                {"erreur": f"Aucun centre de tri avec l'identifiant {centre_tri_id}."},
                status=status.HTTP_404_NOT_FOUND,
            )

        rapport = simuler_comparaison_algorithmes(centre_tri_id=centre_tri_id)
        return Response(rapport, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Scénario 1 — Validation des inscriptions citoyens (dashboard admin)
# ---------------------------------------------------------------------------


class CitoyensEnAttenteView(APIView):
    """
    Must — Gestion des inscriptions : liste des citoyens en attente de validation.

    GET /api/admin/citoyens-enattente/
    Filtre : role=citoyen et is_active=False (Scénario 1 du cahier des charges).
    """

    permission_classes = [IsAuthenticated, IsAdministrateur]

    def get(self, request):
        citoyens = Citoyen.objects.filter(
            role=RoleUtilisateur.CITOYEN,
            is_active=False,
        ).order_by("-date_inscription")
        serializer = CitoyenEnAttenteSerializer(
            citoyens,
            many=True,
            context={"request": request},
        )
        return Response(
            {
                "count": citoyens.count(),
                "resultats": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ValiderCitoyenView(APIView):
    """
    Must — Gestion des inscriptions : activation du compte par l'administrateur.

    PATCH /api/admin/valider-citoyen/<user_id>/
    Passe is_active à True (étape 6 du Scénario 1).
    """

    permission_classes = [IsAuthenticated, IsAdministrateur]

    def patch(self, request, user_id):
        return self._valider(request, user_id)

    def post(self, request, user_id):
        return self._valider(request, user_id)

    def _valider(self, request, user_id):
        try:
            citoyen = Citoyen.objects.get(
                pk=user_id,
                role=RoleUtilisateur.CITOYEN,
            )
        except Citoyen.DoesNotExist:
            return Response(
                {"erreur": f"Aucun citoyen trouvé avec l'identifiant {user_id}."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if citoyen.is_active:
            return Response(
                {"message": "Ce compte est déjà actif."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        citoyen.is_active = True
        citoyen.save(update_fields=["is_active"])

        return Response(
            {
                "message": (
                    f"Inscription de « {citoyen.username} » validée avec succès. "
                    "Le citoyen peut désormais se connecter."
                ),
                "citoyen": CitoyenEnAttenteSerializer(
                    citoyen,
                    context={"request": request},
                ).data,
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# Scénario 2 — Signalements & refus de collecte
# ---------------------------------------------------------------------------


class SignalementViewSet(viewsets.ModelViewSet):
    """
    Must — Signalement citoyen (photo + GPS + type de déchet).

    - CREATE : citoyen connecté (creer_signalement implicite via FK).
    - LIST/RETRIEVE : tout utilisateur authentifié.
    - refuser (action) : chauffeur — variante refus du Scénario 2.
    """

    serializer_class = SignalementSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsCitoyen()]
        if self.action == "refuser":
            return [IsAuthenticated(), IsChauffeur()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return Signalement.objects.select_related("citoyen").order_by("-date_creation")

    def perform_create(self, serializer):
        citoyen = _get_citoyen(self.request.user)
        serializer.save(citoyen=citoyen)

    @action(
        detail=True,
        methods=["post"],
        url_path="refuser",
        parser_classes=[MultiPartParser, FormParser, JSONParser],
    )
    def refuser(self, request, pk=None):
        """
        Scénario 2 (variante) — Le chauffeur refuse la collecte et documente le motif.
        """
        signalement = self.get_object()
        serializer = RefusCollecteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        chauffeur = _get_chauffeur(request.user)
        refus = serializer.save(chauffeur=chauffeur, signalement=signalement)
        refus.enregistrer_refus()

        return Response(
            RefusCollecteSerializer(refus).data,
            status=status.HTTP_201_CREATED,
        )


# ---------------------------------------------------------------------------
# Scénario 3 & Réseau social éco — événements, likes, commentaires
# ---------------------------------------------------------------------------


class EvenementEcologiqueViewSet(viewsets.ModelViewSet):
    """
    Must — Module événements & social.

    - CREATE / UPDATE / DELETE : administrateur (Scénario 3 — création d'événement).
    - participer : citoyen (Scénario 3 — inscription bénévole).
    - commenter / liker : interactions du réseau social éco.
    """

    serializer_class = EvenementEcologiqueSerializer
    queryset = EvenementEcologique.objects.prefetch_related(
        "commentaires__auteur",
        "likes__citoyen",
    ).order_by("-date_evenement")

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAdministrateur()]
        if self.action in ("participer", "liker"):
            return [IsAuthenticated(), IsCitoyen()]
        if self.action == "commenter":
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    @action(detail=True, methods=["post"], url_path="participer")
    def participer(self, request, pk=None):
        """Scénario 3 — Le citoyen clique sur « Participer »."""
        evenement = self.get_object()
        citoyen = _get_citoyen(request.user)
        citoyen.participer_evenement(evenement)
        return Response(
            {
                "message": "Participation enregistrée.",
                "compteur_volontaires": evenement.compteur_volontaires,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="commenter")
    def commenter(self, request, pk=None):
        """Must — Réseau social éco : publication d'un commentaire."""
        evenement = self.get_object()
        serializer = CommentaireCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        commentaire = Commentaire.objects.create(
            evenement=evenement,
            auteur=request.user,
            texte=serializer.validated_data["texte"],
        )
        return Response(
            CommentaireSerializer(commentaire).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="liker")
    def liker(self, request, pk=None):
        """Must — Réseau social éco : like unique par citoyen."""
        evenement = self.get_object()
        citoyen = _get_citoyen(request.user)

        like, cree = InteractionLike.objects.get_or_create(
            evenement=evenement,
            citoyen=citoyen,
        )
        if not cree:
            return Response(
                {"message": "Vous avez déjà liké cet événement."},
                status=status.HTTP_200_OK,
            )
        return Response(
            InteractionLikeSerializer(like).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["delete"], url_path="liker")
    def retirer_like(self, request, pk=None):
        """Retire le like du citoyen connecté sur cet événement."""
        evenement = self.get_object()
        citoyen = _get_citoyen(request.user)
        supprimes, _ = InteractionLike.objects.filter(
            evenement=evenement,
            citoyen=citoyen,
        ).delete()
        if supprimes:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"message": "Aucun like à retirer."},
            status=status.HTTP_404_NOT_FOUND,
        )
