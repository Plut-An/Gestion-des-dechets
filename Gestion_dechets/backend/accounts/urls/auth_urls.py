"""URLs Auth"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views_auth import (
    LoginView,
    RegisterCitoyenView,
    RegisterCamioneurView,
    LogoutView,
    MeView,
    ChangePasswordView,
)

urlpatterns = [
    path('login/',                   LoginView.as_view(),              name='auth-login'),
    path('token/refresh/',           TokenRefreshView.as_view(),       name='auth-token-refresh'),
    path('logout/',                  LogoutView.as_view(),             name='auth-logout'),
    path('register/citoyen/',        RegisterCitoyenView.as_view(),    name='auth-register-citoyen'),
    path('register/camioneur/',      RegisterCamioneurView.as_view(),  name='auth-register-camioneur'),
    path('me/',                      MeView.as_view(),                 name='auth-me'),
    path('change-password/',         ChangePasswordView.as_view(),     name='auth-change-password'),
]
