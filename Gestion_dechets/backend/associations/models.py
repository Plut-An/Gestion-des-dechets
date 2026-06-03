"""
Modèles — associations
"""
from django.db import models
from accounts.models import CustomUser, Citoyen, Camioneur


def logo_upload_path(instance, filename):
    import uuid, os
    ext = filename.split('.')[-1]
    return os.path.join('associations', 'logos', f'{uuid.uuid4()}.{ext}')


class Association(models.Model):
    nom = models.CharField(max_length=150, verbose_name='Nom de l\'association')
    description = models.TextField(blank=True, verbose_name='Description')
    ville = models.CharField(max_length=100, blank=True, verbose_name='Ville')
    logo = models.ImageField(upload_to=logo_upload_path, null=True, blank=True)
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profil_association',
        limit_choices_to={'role': 'association'},
    )
    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Association'
        verbose_name_plural = 'Associations'
        ordering = ['-date_inscription']

    def __str__(self):
        return self.nom


class Adhesion(models.Model):
    """Demande d'un citoyen pour rejoindre une association."""
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé'),
    ]

    citoyen = models.ForeignKey(
        Citoyen,
        on_delete=models.CASCADE,
        related_name='adhesions',
    )
    association = models.ForeignKey(
        Association,
        on_delete=models.CASCADE,
        related_name='adhesions',
    )
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_demande = models.DateTimeField(auto_now_add=True)
    motif_refus = models.TextField(blank=True, verbose_name='Motif de refus')

    class Meta:
        verbose_name = 'Adhésion'
        verbose_name_plural = 'Adhésions'
        unique_together = ('citoyen', 'association')
        ordering = ['-date_demande']

    def __str__(self):
        return f'{self.citoyen.user.nom} → {self.association.nom} [{self.statut}]'


class AcceptationCamioneur(models.Model):
    """Lien entre une association et un camioneur."""
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé'),
    ]

    camioneur = models.ForeignKey(
        Camioneur,
        on_delete=models.CASCADE,
        related_name='liens_associations',
    )
    association = models.ForeignKey(
        Association,
        on_delete=models.CASCADE,
        related_name='camioneurs_lies',
    )
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_demande = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Acceptation camioneur'
        unique_together = ('camioneur', 'association')
        ordering = ['-date_demande']

    def __str__(self):
        return f'{self.camioneur.user.nom} → {self.association.nom} [{self.statut}]'
