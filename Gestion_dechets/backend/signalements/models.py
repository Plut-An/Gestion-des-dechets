"""
Modèles — signalements
"""
import os, uuid
from django.db import models
from accounts.models import Citoyen, Camioneur


def photo_signalement_path(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join('signalements', f'{uuid.uuid4()}.{ext}')


class Signalement(models.Model):
    TYPE_DECHET_CHOICES = [
        ('organique', 'Organique'),
        ('plastique', 'Plastique'),
        ('verre', 'Verre'),
        ('metal', 'Métal'),
        ('mixte', 'Mixte'),
        ('autre', 'Autre'),
    ]
    STATUT_CHOICES = [
        ('signale', 'Signalé'),
        ('assigne', 'Assigné à un camioneur'),
        ('en_cours', 'En cours de collecte'),
        ('traite', 'Traité'),
        ('refuse', 'Refusé'),
    ]

    citoyen = models.ForeignKey(
        Citoyen,
        on_delete=models.SET_NULL,
        null=True,
        related_name='signalements',
    )
    photo = models.ImageField(
        upload_to=photo_signalement_path,
        null=True, blank=True,
        verbose_name='Photo du déchet',
    )
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    description = models.TextField(blank=True, verbose_name='Description')
    type_dechet = models.CharField(
        max_length=20, choices=TYPE_DECHET_CHOICES, default='autre'
    )
    statut = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default='signale'
    )
    camioneur_assigne = models.ForeignKey(
        Camioneur,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='signalements_assignes',
    )
    date_signalement = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Signalement'
        verbose_name_plural = 'Signalements'
        ordering = ['-date_signalement']

    def __str__(self):
        citoyen_nom = self.citoyen.user.nom if self.citoyen else 'Inconnu'
        return f'Signalement #{self.pk} par {citoyen_nom} [{self.statut}]'
