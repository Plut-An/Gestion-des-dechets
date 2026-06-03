"""
Admin — associations
"""
from django.contrib import admin
from .models import Association, Adhesion, AcceptationCamioneur


@admin.register(Association)
class AssociationAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ville', 'date_inscription')
    search_fields = ('nom', 'ville')


@admin.register(Adhesion)
class AdhesionAdmin(admin.ModelAdmin):
    list_display = ('citoyen', 'association', 'statut', 'date_demande')
    list_filter = ('statut',)


@admin.register(AcceptationCamioneur)
class AcceptationCamioneurAdmin(admin.ModelAdmin):
    list_display = ('camioneur', 'association', 'statut', 'date_demande')
    list_filter = ('statut',)
