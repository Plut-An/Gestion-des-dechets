"""URLs — associations"""
from django.urls import path
from .views import (
    AssociationListView,
    AssociationMembreListView,
    AdhesionListView,
    AdhesionActionView,
    CamioneurAssociationListView,
    CamioneurAssociationActionView,
    RejoindreAssociationView,
)

urlpatterns = [
    # Public / mobile citoyen
    path('',                                                        AssociationListView.as_view(),              name='associations-list'),
    path('<int:pk>/rejoindre/',                                     RejoindreAssociationView.as_view(),         name='associations-rejoindre'),

    # Espace web — gestion membres
    path('membres/',                                                AssociationMembreListView.as_view(),        name='associations-membres'),
    path('adhesions/',                                              AdhesionListView.as_view(),                 name='associations-adhesions'),
    path('adhesions/<int:adhesion_id>/action/',                     AdhesionActionView.as_view(),               name='associations-adhesion-action'),

    # Espace web — gestion camioneurs
    path('camioneurs/',                                             CamioneurAssociationListView.as_view(),     name='associations-camioneurs'),
    path('camioneurs/<int:camioneur_id>/action/',                   CamioneurAssociationActionView.as_view(),   name='associations-camioneur-action'),
]
