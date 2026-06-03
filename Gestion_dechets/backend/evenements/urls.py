"""URLs — evenements"""
from django.urls import path
from .views import (
    AnnonceListCreateView,
    AnnonceDetailView,
    EvenementListCreateView,
    EvenementDetailView,
    EvenementParticipantsView,
    ConfirmerPresenceView,
    MobileEvenementListView,
    MobileAnnonceListView,
    ParticiperEvenementView,
    MesParticipationsView,
    CommentaireListCreateView,
    CommentaireDeleteView,
)

urlpatterns = [
    # Association web — annonces
    path('association/annonces/',
         AnnonceListCreateView.as_view(), name='annonces-list'),
    path('association/annonces/<int:pk>/',
         AnnonceDetailView.as_view(), name='annonces-detail'),

    # Association web — événements
    path('association/evenements/',
         EvenementListCreateView.as_view(), name='evenements-list'),
    path('association/evenements/<int:pk>/',
         EvenementDetailView.as_view(), name='evenements-detail'),
    path('association/evenements/<int:ev_pk>/participants/',
         EvenementParticipantsView.as_view(), name='evenements-participants'),
    path('association/evenements/<int:ev_pk>/participants/<int:participation_id>/confirmer/',
         ConfirmerPresenceView.as_view(), name='evenements-confirmer-presence'),

    # Mobile — citoyen
    path('evenements/',                             MobileEvenementListView.as_view(),  name='mobile-evenements'),
    path('evenements/<int:ev_pk>/participer/',      ParticiperEvenementView.as_view(),  name='mobile-participer'),
    path('evenements/<int:ev_pk>/commentaires/',    CommentaireListCreateView.as_view(),name='mobile-commentaires'),
    path('commentaires/<int:pk>/',                  CommentaireDeleteView.as_view(),    name='mobile-commentaires-delete'),
    path('evenements/mes-participations/',          MesParticipationsView.as_view(),    name='mobile-mes-participations'),
    path('annonces/',                               MobileAnnonceListView.as_view(),    name='mobile-annonces'),
]
