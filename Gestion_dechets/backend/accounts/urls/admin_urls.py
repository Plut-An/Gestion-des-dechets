"""URLs Admin"""
from django.urls import path
from accounts.views_admin import (
    DashboardView,
    CitoyenListCreateView,
    CitoyenDetailView,
    ValiderCitoyenView,
    CamioneurListCreateView,
    CamioneurDetailView,
    ValiderCamioneurView,
)
from associations.views import AdminAssociationListCreateView, AdminAssociationDetailView

urlpatterns = [
    # Dashboard
    path('dashboard/',                          DashboardView.as_view(),                name='admin-dashboard'),

    # Citoyens
    path('citoyens/',                           CitoyenListCreateView.as_view(),         name='admin-citoyens-list'),
    path('citoyens/<int:pk>/',                  CitoyenDetailView.as_view(),             name='admin-citoyens-detail'),
    path('citoyens/<int:pk>/valider/',          ValiderCitoyenView.as_view(),            name='admin-citoyens-valider'),

    # Camioneurs
    path('camioneurs/',                         CamioneurListCreateView.as_view(),       name='admin-camioneurs-list'),
    path('camioneurs/<int:pk>/',                CamioneurDetailView.as_view(),           name='admin-camioneurs-detail'),
    path('camioneurs/<int:pk>/valider/',        ValiderCamioneurView.as_view(),          name='admin-camioneurs-valider'),

    # Associations
    path('associations/',                       AdminAssociationListCreateView.as_view(), name='admin-associations-list'),
    path('associations/<int:pk>/',              AdminAssociationDetailView.as_view(),     name='admin-associations-detail'),
]
