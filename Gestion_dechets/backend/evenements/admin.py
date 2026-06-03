"""Admin — evenements"""
from django.contrib import admin
from .models import Annonce, EvenementEcologique, Participation


@admin.register(Annonce)
class AnnonceAdmin(admin.ModelAdmin):
    list_display = ('titre', 'association', 'type', 'date_publication')
    list_filter = ('type', 'association')
    search_fields = ('titre', 'association__nom')


@admin.register(EvenementEcologique)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ('titre', 'association', 'date_evenement', 'statut')
    list_filter = ('statut', 'association')
    search_fields = ('titre', 'association__nom', 'lieu')


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('citoyen', 'evenement', 'date_participation', 'presence_confirmee')
    list_filter = ('presence_confirmee',)
