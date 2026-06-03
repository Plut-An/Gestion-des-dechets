"""Admin — signalements"""
from django.contrib import admin
from .models import Signalement


@admin.register(Signalement)
class SignalementAdmin(admin.ModelAdmin):
    list_display = ('id', 'citoyen', 'type_dechet', 'statut', 'camioneur_assigne', 'date_signalement')
    list_filter = ('statut', 'type_dechet')
    search_fields = ('citoyen__user__nom', 'description')
    readonly_fields = ('date_signalement', 'date_modification')
