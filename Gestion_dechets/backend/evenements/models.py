"""
Modèles — evenements
"""
import os, uuid
from django.db import models
from associations.models import Association
from accounts.models import Citoyen


def annonce_image_path(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join('annonces', f'{uuid.uuid4()}.{ext}')


class Annonce(models.Model):
    """Publication d'une association : annonce ou contenu partagé."""
    TYPE_CHOICES = [
        ('annonce', 'Annonce'),
        ('contenu_partage', 'Contenu partagé'),
    ]

    association = models.ForeignKey(
        Association,
        on_delete=models.CASCADE,
        related_name='annonces',
    )
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    image = models.ImageField(upload_to=annonce_image_path, null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='annonce')
    date_publication = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Annonce'
        verbose_name_plural = 'Annonces'
        ordering = ['-date_publication']

    def __str__(self):
        return f'[{self.association.nom}] {self.titre}'


class EvenementEcologique(models.Model):
    """Événement organisé par une association pour la manifestation d'intérêt."""
    STATUT_CHOICES = [
        ('a_venir', 'À venir'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
    ]

    association = models.ForeignKey(
        Association,
        on_delete=models.CASCADE,
        related_name='evenements',
    )
    titre = models.CharField(max_length=200)
    description = models.TextField()
    date_evenement = models.DateTimeField()
    lieu = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='a_venir')
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Événement écologique'
        verbose_name_plural = 'Événements écologiques'
        ordering = ['-date_evenement']

    def __str__(self):
        return f'[{self.association.nom}] {self.titre}'

    @property
    def compteur_volontaires(self):
        return self.participations.filter(presence_confirmee=False).count()

    @property
    def compteur_presents(self):
        return self.participations.filter(presence_confirmee=True).count()


class Participation(models.Model):
    """Un citoyen s'inscrit à un événement."""
    citoyen = models.ForeignKey(
        Citoyen,
        on_delete=models.CASCADE,
        related_name='participations',
    )
    evenement = models.ForeignKey(
        EvenementEcologique,
        on_delete=models.CASCADE,
        related_name='participations',
    )
    date_participation = models.DateTimeField(auto_now_add=True)
    presence_confirmee = models.BooleanField(
        default=False,
        verbose_name='Présence confirmée par l\'association',
    )

    class Meta:
        verbose_name = 'Participation'
        verbose_name_plural = 'Participations'
        unique_together = ('citoyen', 'evenement')
        ordering = ['-date_participation']

    def __str__(self):
        return f'{self.citoyen.user.nom} → {self.evenement.titre}'


class Commentaire(models.Model):
    """Commentaire sur un événement écologique."""
    evenement = models.ForeignKey(
        EvenementEcologique,
        on_delete=models.CASCADE,
        related_name='commentaires',
    )
    auteur = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='commentaires',
    )
    contenu = models.TextField()
    date_publication = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Commentaire'
        verbose_name_plural = 'Commentaires'
        ordering = ['date_publication']

    def __str__(self):
        return f'Commentaire de {self.auteur.nom} sur {self.evenement.titre}'
