"""
Admin configuration — accounts
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Citoyen, Camioneur


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    ordering = ('-date_creation',)
    list_display = ('email', 'nom', 'role', 'is_active', 'date_creation')
    list_filter = ('role', 'is_active')
    search_fields = ('email', 'nom')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informations personnelles'), {'fields': ('nom', 'role', 'langue')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Dates'), {'fields': ('last_login', 'date_creation')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nom', 'role', 'password1', 'password2'),
        }),
    )
    readonly_fields = ('date_creation',)


@admin.register(Citoyen)
class CitoyenAdmin(admin.ModelAdmin):
    list_display = ('user', 'solde_eco_points', 'statut_inscription')
    list_filter = ('statut_inscription',)
    search_fields = ('user__nom', 'user__email')


@admin.register(Camioneur)
class CamioneurAdmin(admin.ModelAdmin):
    list_display = ('user', 'numero_permis', 'disponible', 'statut_inscription')
    list_filter = ('disponible', 'statut_inscription')
    search_fields = ('user__nom', 'user__email', 'numero_permis')
