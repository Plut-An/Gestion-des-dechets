"""URLs — collectes"""
from django.urls import path
from .views import (
    MettreAJourPositionView,
    HistoriquePositionView,
    ProfilCamioneurView,
    AdminCamioneurPositionsView,
)

urlpatterns = [
    # Mobile — Camioneur
    path('camioneur/position/',         MettreAJourPositionView.as_view(),      name='camioneur-position'),
    path('camioneur/position/history/', HistoriquePositionView.as_view(),       name='camioneur-position-history'),
    path('camioneur/profil/',           ProfilCamioneurView.as_view(),          name='camioneur-profil'),

    # Admin
    path('admin-camioneurs/carte/',     AdminCamioneurPositionsView.as_view(),  name='admin-camioneurs-carte'),
]
