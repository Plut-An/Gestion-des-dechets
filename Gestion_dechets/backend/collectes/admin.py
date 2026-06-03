"""Admin — collectes"""
from django.contrib import admin
from .models import PositionCamioneur


@admin.register(PositionCamioneur)
class PositionCamioneurAdmin(admin.ModelAdmin):
    list_display = ('camioneur', 'latitude', 'longitude', 'horodatage')
    list_filter = ('camioneur',)
    readonly_fields = ('horodatage',)
