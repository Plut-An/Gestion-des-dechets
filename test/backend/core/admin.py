from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Bareme,
    Camion,
    CentreDeTri,
    Chauffeur,
    Citoyen,
    DepotDechet,
    EvenementEcologique,
    PointDeCollecte,
    RefusCollecte,
    Route,
    Signalement,
    Tournee,
    Utilisateur,
)


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_staff", "date_inscription")
    list_filter = ("role", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Profil métier", {"fields": ("nom_utilisateur", "role", "date_inscription")}),
    )


@admin.register(Citoyen)
class CitoyenAdmin(UserAdmin):
    list_display = ("username", "email", "solde_eco_points")


@admin.register(Chauffeur)
class ChauffeurAdmin(UserAdmin):
    list_display = ("username", "numero_permis", "disponibilite")


admin.site.register(PointDeCollecte)
admin.site.register(CentreDeTri)
admin.site.register(Bareme)
admin.site.register(DepotDechet)
admin.site.register(Route)
admin.site.register(Camion)
admin.site.register(Tournee)
admin.site.register(Signalement)
admin.site.register(RefusCollecte)
admin.site.register(EvenementEcologique)
