"""
URL configuration — Phase 0 routing map.

Public: /, /categories, /legal/*
Authenticated: /app/*, /settings/*
Staff only: /admin
Legacy marketplace modules (providers, reviews, bcubed) stay mounted for
later phases and are not linked from the Phase 0 shell.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.foundation import views as foundation_views

urlpatterns = [
    # Staff only (server-side is_staff check)
    path('admin/', admin.site.urls),

    # Phase 0 routing map
    path('', include('apps.foundation.urls')),
    path('', include('apps.core.urls')),

    # Auth (email)
    path('accounts/', include('apps.accounts.urls')),

    # Legacy marketplace modules — rebuilt in later phases
    path('providers/', include('apps.providers.urls')),
    path('reviews/', include('apps.reviews.urls')),
    path('bcubed/', include('apps.bcubed.urls', namespace='bcubed')),

    # API
    path('api/', include('apps.providers.api_urls')),
    path('api/', include('apps.reviews.api_urls')),
]

handler403 = 'apps.foundation.views.permission_denied'
handler404 = 'apps.foundation.views.page_not_found'
handler500 = 'apps.foundation.views.server_error'

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
