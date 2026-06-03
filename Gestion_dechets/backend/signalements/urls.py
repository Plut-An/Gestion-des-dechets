"""URLs — signalements"""
from django.urls import path
from .views import (
    CitoyenSignalementListCreateView,
    CitoyenSignalementDetailView,
    CamioneurSignalementsProchesView,
    CamioneurAccepterSignalementView,
    CamioneurValiderSignalementView,
    CamioneurRefuserSignalementView,
    CamioneurMesCollectesView,
    AdminSignalementListView,
)

urlpatterns = [
    # Mobile — Citoyen
    path('signalements/',                               CitoyenSignalementListCreateView.as_view(),     name='signalements-list'),
    path('signalements/<int:pk>/',                      CitoyenSignalementDetailView.as_view(),         name='signalements-detail'),

    # Mobile — Camioneur
    path('camioneur/signalements/',                     CamioneurSignalementsProchesView.as_view(),     name='camioneur-signalements-proches'),
    path('camioneur/signalements/<int:pk>/accepter/',   CamioneurAccepterSignalementView.as_view(),     name='camioneur-accepter'),
    path('camioneur/signalements/<int:pk>/valider/',    CamioneurValiderSignalementView.as_view(),      name='camioneur-valider'),
    path('camioneur/signalements/<int:pk>/refuser/',    CamioneurRefuserSignalementView.as_view(),      name='camioneur-refuser'),
    path('camioneur/collectes/',                        CamioneurMesCollectesView.as_view(),            name='camioneur-collectes'),

    # Admin
    path('admin-signalements/',                         AdminSignalementListView.as_view(),             name='admin-signalements'),
]
