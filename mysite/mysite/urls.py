"""
Конфигурация URL для проекта mysite.

Список `urlpatterns` направляет URL к представлениям.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from django.conf.urls.i18n import i18n_patterns

from drf_spectacular.views import (SpectacularAPIView,
                                   SpectacularRedocView,
                                   SpectacularSwaggerView)

# Базовые URL паттерны
urlpatterns = [
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    path('req/', include('requestdataapp.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/', include('myapiapp.urls')),
]

# URL паттерны с поддержкой интернационализации
urlpatterns += i18n_patterns(
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('blog/', include('blogapp.urls')),
    path('accounts/', include('myauth.urls')),
    path('shop/', include('shopapp.urls')),
)

# Отладочные URL только в режиме DEBUG
if settings.DEBUG:
    # Обслуживание медиа файлов
    urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))

    # Обслуживание статических файлов
    urlpatterns.extend(static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))

    # URL для Django Debug Toolbar
    urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')))
