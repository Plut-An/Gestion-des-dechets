"""
URL configuration — Gestion des Déchets API
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Django admin
    path('django-admin/', admin.site.urls),

    # API schema & documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Auth
    path('api/auth/', include('accounts.urls.auth_urls')),

    # Admin endpoints
    path('api/admin/', include('accounts.urls.admin_urls')),

    # Associations (espace web)
    path('api/associations/', include('associations.urls')),

    # Mobile — Citoyen & Camioneur
    path('api/mobile/', include('signalements.urls')),
    path('api/mobile/', include('evenements.urls')),
    path('api/mobile/', include('collectes.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
