"""
Настройки Django для проекта mysite.

Сгенерировано с помощью 'django-admin startproject' используя Django 5.2.6.
"""

import os
from pathlib import Path

from django.conf.global_settings import CACHE_MIDDLEWARE_SECONDS
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as gettext

import sentry_sdk

# Инициализация Sentry для мониторинга ошибок
sentry_sdk.init(
    dsn="https://81ad8ec189c87bcb436810990a22ff5e@o4510182655983616.ingest.us.sentry.io/4510353698586624",
    traces_sample_rate=1.0,
    send_default_pii=True,
)

# Базовый путь проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Настройки безопасности
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-shpni&6)!ss''(b=-^bk2o4-t-sm$5c5dpah__xm)93@uuat%uz*')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# Разрешенные хосты для Docker
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '0.0.0.0,127.0.0.1,localhost').split(',')

# Внутренние IP-адреса для Django Debug Toolbar
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
    '172.17.0.1',  # Docker внутренний адрес
]

# Автоматическое определение IP-адресов для Debug Toolbar в режиме отладки
if DEBUG:
    import socket
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS.append('10.0.2.2')
    INTERNAL_IPS.extend([ip[: ip.rfind('.')] + '.1' for ip in ips])
    try:
        INTERNAL_IPS.append(socket.gethostbyname(hostname))
    except:
        pass

# Установленные приложения
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admindocs',
    'django.contrib.sitemaps',

    # Сторонние приложения
    'debug_toolbar',  # Инструменты отладки Django
    'rest_framework',  # Django REST Framework
    'django_filters',  # Фильтрация для DRF
    'drf_spectacular',  # Генерация документации OpenAPI

    # Пользовательские приложения
    'blogapp',
    'shopapp.apps.ShopappConfig',
    'requestdataapp.apps.RequestdataappConfig',
    'myauth.apps.MyauthConfig',
    'myapiapp.apps.MyapiappConfig'
]

# Промежуточное ПО
MIDDLEWARE = [
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'requestdataapp.middlewares.setup_useragent_on_request_middleware',
    'requestdataapp.middlewares.CountRequestMiddleware',
    'requestdataapp.middlewares.ThrottlingMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
]

# Конфигурация URL
ROOT_URLCONF = 'mysite.urls'

# Конфигурация шаблонов
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'

# Настройки базы данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'database' / 'db.sqlite3',  # Прямой путь
        'OPTIONS': {
            'timeout': 30,
            'check_same_thread': False,
        },
        'ATOMIC_REQUESTS': False,
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        # 'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        # 'LOCATION': '/var/tmp/django_cache',
    },
}

CACHE_MIDDLEWARE_SECONDS = 200

# Валидаторы паролей
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Международные настройки
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
USE_L10N = True

LOCALE_PATHS = [BASE_DIR / 'locale/']
LANGUAGES = [
    ('en', gettext('English')),
    ('ru', gettext('Russian')),
]

# Статические файлы и медиа
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'uploads'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Настройки аутентификации
LOGIN_REDIRECT_URL = reverse_lazy("myauth:about-me")
LOGIN_URL = reverse_lazy("myauth:login")

# Настройки логирования для Docker
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'shopapp': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# Настройки Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Настройки drf-spectacular для генерации OpenAPI схемы
SPECTACULAR_SETTINGS = {
    'TITLE': 'My Site Project API',
    'DESCRIPTION': 'My site with shop app and custom auth',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Настройки сессий для избежания блокировок базы данных
SESSION_ENGINE = 'django.contrib.sessions.backends.file'
SESSION_FILE_PATH = '/tmp/django_sessions'
SESSION_COOKIE_AGE = 3600  # 1 час
SESSION_SAVE_EVERY_REQUEST = False

# Создание директории для сессий если не существует
if not os.path.exists('/tmp/django_sessions'):
    os.makedirs('/tmp/django_sessions', exist_ok=True)

# Конфигурация Django Debug Toolbar
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
}
