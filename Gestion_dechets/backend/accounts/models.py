"""
Modèles accounts — CustomUser, Citoyen, Camioneur
"""
import os
import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


def profil_photo_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('profils', filename)


class CustomUserManager(BaseUserManager):
    """Manager personnalisé — email remplace username."""

    def create_user(self, email, nom, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire.")
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, nom=nom, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nom, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, nom, password, **extra_fields)


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('citoyen', 'Citoyen'),
        ('camioneur', 'Camioneur'),
        ('association', 'Association'),
    ]
    LANGUE_CHOICES = [
        ('FR', 'Français'),
        ('MG', 'Malagasy'),
    ]

    # On utilise l'email comme identifiant
    username = None
    email = models.EmailField(unique=True, verbose_name='Adresse email')
    nom = models.CharField(max_length=150, verbose_name='Nom complet')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='citoyen')
    langue = models.CharField(max_length=2, choices=LANGUE_CHOICES, default='FR')
    date_creation = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom']

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['-date_creation']

    def __str__(self):
        return f'{self.nom} ({self.email}) — {self.get_role_display()}'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_citoyen(self):
        return self.role == 'citoyen'

    @property
    def is_camioneur(self):
        return self.role == 'camioneur'


class Citoyen(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé'),
    ]

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profil_citoyen',
        limit_choices_to={'role': 'citoyen'},
    )
    solde_eco_points = models.IntegerField(default=0, verbose_name='Eco-Points')
    photo_profil = models.ImageField(
        upload_to=profil_photo_path,
        null=True, blank=True,
        verbose_name='Photo de profil',
    )
    adresse = models.TextField(blank=True, verbose_name='Adresse')
    statut_inscription = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default='en_attente'
    )
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Citoyen'
        verbose_name_plural = 'Citoyens'

    def __str__(self):
        return f'Citoyen: {self.user.nom}'


class Camioneur(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé'),
    ]

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profil_camioneur',
        limit_choices_to={'role': 'camioneur'},
    )
    solde_eco_points = models.IntegerField(default=0, verbose_name='Eco-Points')
    numero_permis = models.CharField(max_length=50, verbose_name='Numéro de permis')
    disponible = models.BooleanField(default=False, verbose_name='Disponible')
    latitude_actuelle = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True
    )
    longitude_actuelle = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )
    statut_inscription = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default='en_attente'
    )
    mot_de_passe_temporaire = models.BooleanField(
        default=True,
        verbose_name='Doit changer son mot de passe',
    )
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Camioneur'
        verbose_name_plural = 'Camioneurs'

    def __str__(self):
        return f'Camioneur: {self.user.nom}'
