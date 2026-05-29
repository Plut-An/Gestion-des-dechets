"""
Modèles du domaine « Gestion des déchets » — traduction du diagramme de classes.
"""
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class RoleUtilisateur(models.TextChoices):
    """Rôles métier (administrateur géré via is_staff sur Utilisateur)."""

    CITOYEN = "citoyen", "Citoyen"
    CHAUFFEUR = "chauffeur", "Chauffeur"
    ADMINISTRATEUR = "administrateur", "Administrateur"


class Utilisateur(AbstractUser):
    """Utilisateur de la plateforme (hérite d'AbstractUser)."""

    nom_utilisateur = models.CharField(
        "nom d'utilisateur affiché",
        max_length=150,
        blank=True,
    )
    role = models.CharField(
        max_length=20,
        choices=RoleUtilisateur.choices,
        default=RoleUtilisateur.CITOYEN,
    )
    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"

    def se_connecter(self) -> bool:
        """Connexion gérée par Django Auth (login view / JWT)."""
        return self.is_active

    def se_deconnecter(self) -> bool:
        """Déconnexion gérée par Django Auth (logout view)."""
        return True

    def modifier_profil(self, **champs) -> bool:
        """Met à jour les champs du profil fournis."""
        for cle, valeur in champs.items():
            if hasattr(self, cle):
                setattr(self, cle, valeur)
        self.save()
        return True


class Citoyen(Utilisateur):
    """Citoyen inscrit sur la plateforme."""

    solde_eco_points = models.PositiveIntegerField(default=0)
    piece_identite = models.FileField(
        upload_to="justificatifs/id/",
        blank=True,
        null=True,
    )
    certificat_residence = models.FileField(
        upload_to="justificatifs/residence/",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "citoyen"
        verbose_name_plural = "citoyens"

    def creer_compte(self) -> bool:
        """Création du compte (formulaire d'inscription + validation admin)."""
        self.role = RoleUtilisateur.CITOYEN
        self.is_active = False
        self.save()
        return True

    def creer_signalement(self, **donnees) -> "Signalement":
        """Crée un signalement lié à ce citoyen."""
        return Signalement.objects.create(citoyen=self, **donnees)

    def participer_evenement(self, evenement: "EvenementEcologique") -> bool:
        """Inscrit le citoyen à un événement écologique."""
        evenement.participants.add(self)
        evenement.compteur_volontaires = evenement.participants.count()
        evenement.save(update_fields=["compteur_volontaires"])
        return True


class Chauffeur(Utilisateur):
    """Chauffeur de camion de collecte."""

    numero_permis = models.CharField(max_length=50, unique=True)
    disponibilite = models.BooleanField(default=True)

    class Meta:
        verbose_name = "chauffeur"
        verbose_name_plural = "chauffeurs"

    def valider_collecte(self, depot: "DepotDechet") -> bool:
        """Valide un dépôt de déchet et attribue les points."""
        depot.chauffeur_validateur = self
        depot.save(update_fields=["chauffeur_validateur_id"])
        depot.calculer_points()
        return True

    def refuser_collecte(self, signalement: "Signalement", motif: str, photo: str = "") -> "RefusCollecte":
        """Enregistre un refus de collecte pour un signalement."""
        return RefusCollecte.objects.create(
            chauffeur=self,
            signalement=signalement,
            motif_ecrit=motif,
            photo_justificative=photo,
        )


class Noeud(models.Model):
    """Nœud géographique du réseau (parent de PointDeCollecte et CentreDeTri)."""

    latitude = models.FloatField()
    longitude = models.FloatField()
    nom_lieu = models.CharField(max_length=255)

    class Meta:
        verbose_name = "nœud"
        verbose_name_plural = "nœuds"

    def __str__(self) -> str:
        return self.nom_lieu


class PointDeCollecte(Noeud):
    """Bac ou point de collecte sur le territoire."""

    class TypeBac(models.TextChoices):
        MENAGER = "menager", "Ménager"
        RECYCLABLE = "recyclable", "Recyclable"
        VERRE = "verre", "Verre"
        ORGANIQUE = "organique", "Organique"

    type_bac = models.CharField(max_length=20, choices=TypeBac.choices)
    capacite_bacs = models.PositiveIntegerField(default=1)
    etat_remplissage = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Pourcentage de remplissage (0-100).",
    )
    est_prioritaire = models.BooleanField(default=False)
    etat_proprete_alentours = models.CharField(max_length=100, blank=True)
    date_derniere_collecte = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "point de collecte"
        verbose_name_plural = "points de collecte"


class CentreDeTri(Noeud):
    """Centre de tri / destination des tournées."""

    capacite_max = models.FloatField(help_text="Capacité maximale en tonnes.")
    stock_actuel = models.FloatField(default=0.0, help_text="Stock actuel en tonnes.")

    class Meta:
        verbose_name = "centre de tri"
        verbose_name_plural = "centres de tri"

    def mettre_a_jour_stock(self, quantite: float = 0.0) -> bool:
        """Met à jour le stock en ajoutant une quantité (tonnes)."""
        self.stock_actuel = min(self.capacite_max, self.stock_actuel + quantite)
        self.save(update_fields=["stock_actuel"])
        return True


class Bareme(models.Model):
    """Barème d'attribution des eco-points par type de matériau."""

    type_materiau = models.CharField(max_length=100, unique=True)
    points_par_kg = models.PositiveIntegerField()

    class Meta:
        verbose_name = "barème"
        verbose_name_plural = "barèmes"

    def __str__(self) -> str:
        return f"{self.type_materiau} ({self.points_par_kg} pts/kg)"


class DepotDechet(models.Model):
    """Dépôt de déchet trié par un citoyen, validé par un chauffeur."""

    citoyen = models.ForeignKey(
        Citoyen,
        on_delete=models.CASCADE,
        related_name="depots",
    )
    bareme = models.ForeignKey(
        Bareme,
        on_delete=models.PROTECT,
        related_name="depots",
    )
    chauffeur_validateur = models.ForeignKey(
        Chauffeur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="depots_valides",
    )
    poids = models.FloatField(help_text="Poids en kg.")
    points_attribues = models.PositiveIntegerField(default=0)
    date_depot = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "dépôt de déchet"
        verbose_name_plural = "dépôts de déchets"

    def calculer_points(self) -> int:
        """Calcule et enregistre les points selon le barème, puis crédite le citoyen."""
        if self.bareme_id and self.poids:
            self.points_attribues = int(self.poids * self.bareme.points_par_kg)
            self.save(update_fields=["points_attribues"])
            self.citoyen.solde_eco_points += self.points_attribues
            self.citoyen.save(update_fields=["solde_eco_points"])
        return self.points_attribues


class Route(models.Model):
    """Arête du graphe routier entre deux nœuds."""

    depart = models.ForeignKey(
        Noeud,
        on_delete=models.CASCADE,
        related_name="routes_depart",
    )
    arrivee = models.ForeignKey(
        Noeud,
        on_delete=models.CASCADE,
        related_name="routes_arrivee",
    )
    distance = models.FloatField(help_text="Distance en km.")
    poids = models.FloatField(
        default=1.0,
        help_text="Poids pour l'algorithme de plus court chemin (Dijkstra/A*).",
    )

    class Meta:
        verbose_name = "route"
        verbose_name_plural = "routes"
        constraints = [
            models.UniqueConstraint(
                fields=["depart", "arrivee"],
                name="unique_route_depart_arrivee",
            ),
        ]


class Camion(models.Model):
    """Véhicule de collecte."""

    immatriculation = models.CharField(max_length=20, unique=True)
    gabarit = models.CharField(max_length=50)
    capacite_max = models.FloatField(help_text="Capacité maximale en tonnes.")
    charge_actuelle = models.FloatField(default=0.0)
    chauffeur = models.OneToOneField(
        Chauffeur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="camion",
    )

    class Meta:
        verbose_name = "camion"
        verbose_name_plural = "camions"

    def __str__(self) -> str:
        return self.immatriculation


class Tournee(models.Model):
    """Tournée de collecte optimisée."""

    class StatutTournee(models.TextChoices):
        PLANIFIEE = "planifiee", "Planifiée"
        EN_COURS = "en_cours", "En cours"
        TERMINEE = "terminee", "Terminée"
        ANNULEE = "annulee", "Annulée"

    camion = models.ForeignKey(
        Camion,
        on_delete=models.CASCADE,
        related_name="tournees",
    )
    destination = models.ForeignKey(
        CentreDeTri,
        on_delete=models.PROTECT,
        related_name="tournees",
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=20,
        choices=StatutTournee.choices,
        default=StatutTournee.PLANIFIEE,
    )
    chemin_ordonne = models.JSONField(
        default=list,
        blank=True,
        help_text="Liste ordonnée d'identifiants de nœuds (itinéraire optimisé).",
    )

    class Meta:
        verbose_name = "tournée"
        verbose_name_plural = "tournées"


class Signalement(models.Model):
    """Signalement citoyen (bac plein, dépôt sauvage, etc.)."""

    class StatutSignalement(models.TextChoices):
        EN_ATTENTE = "en_attente", "En attente"
        EN_COURS = "en_cours", "En cours de traitement"
        RESOLU = "resolu", "Résolu"
        REFUSE = "refuse", "Refusé"

    citoyen = models.ForeignKey(
        Citoyen,
        on_delete=models.CASCADE,
        related_name="signalements",
    )
    photo = models.ImageField(upload_to="signalements/", blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    type_dechet = models.CharField(max_length=100)
    statut = models.CharField(
        max_length=20,
        choices=StatutSignalement.choices,
        default=StatutSignalement.EN_ATTENTE,
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "signalement"
        verbose_name_plural = "signalements"


class RefusCollecte(models.Model):
    """Refus de collecte émis par un chauffeur."""

    chauffeur = models.ForeignKey(
        Chauffeur,
        on_delete=models.CASCADE,
        related_name="refus",
    )
    signalement = models.OneToOneField(
        Signalement,
        on_delete=models.CASCADE,
        related_name="refus",
        null=True,
        blank=True,
    )
    motif_ecrit = models.TextField()
    photo_justificative = models.ImageField(
        upload_to="refus/",
        blank=True,
    )
    date_refus = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "refus de collecte"
        verbose_name_plural = "refus de collecte"

    def enregistrer_refus(self) -> bool:
        """Persiste le refus et met à jour le statut du signalement."""
        self.save()
        if self.signalement_id:
            self.signalement.statut = Signalement.StatutSignalement.REFUSE
            self.signalement.save(update_fields=["statut"])
        return True


class EvenementEcologique(models.Model):
    """Événement du réseau social éco."""

    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date_evenement = models.DateTimeField()
    lieu = models.CharField(max_length=255, blank=True)
    compteur_volontaires = models.PositiveIntegerField(default=0)
    participants = models.ManyToManyField(
        Citoyen,
        related_name="evenements",
        blank=True,
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "événement écologique"
        verbose_name_plural = "événements écologiques"

    def __str__(self) -> str:
        return self.titre


class Commentaire(models.Model):
    """Commentaire sur un événement du réseau social éco."""

    evenement = models.ForeignKey(
        EvenementEcologique,
        on_delete=models.CASCADE,
        related_name="commentaires",
    )
    auteur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name="commentaires",
    )
    texte = models.TextField()
    date_publication = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "commentaire"
        verbose_name_plural = "commentaires"


class InteractionLike(models.Model):
    """Like d'un citoyen sur un événement écologique."""

    evenement = models.ForeignKey(
        EvenementEcologique,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    citoyen = models.ForeignKey(
        Citoyen,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    date_like = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "like"
        verbose_name_plural = "likes"
        constraints = [
            models.UniqueConstraint(
                fields=["evenement", "citoyen"],
                name="unique_like_evenement_citoyen",
            ),
        ]
