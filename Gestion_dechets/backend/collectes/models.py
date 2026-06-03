"""
Modèles — collectes (position GPS temps réel du camioneur)
"""
from django.db import models
from accounts.models import Camioneur


class PositionCamioneur(models.Model):
    """
    Historique des positions GPS du camioneur.
    Permet de tracer l'itinéraire et de retrouver la dernière position connue.
    """
    camioneur = models.ForeignKey(
        Camioneur,
        on_delete=models.CASCADE,
        related_name='positions',
    )
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    horodatage = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Position camioneur'
        verbose_name_plural = 'Positions camioneurs'
        ordering = ['-horodatage']
        # Garder seulement les 500 dernières positions par camioneur (géré dans la view)
        indexes = [
            models.Index(fields=['camioneur', '-horodatage']),
        ]

    def __str__(self):
        return f'{self.camioneur.user.nom} @ ({self.latitude}, {self.longitude}) — {self.horodatage}'
