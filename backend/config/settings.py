"""
Django settings for RescueMesh Mission Platform.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Docker environment detection
RUNNING_IN_DOCKER = os.path.exists('/.dockerenv')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# GIS libraries (PostGIS support)
GEOS_LIBRARY_PATH = os.environ.get('GEOS_LIBRARY_PATH')
GDAL_LIBRARY_PATH = os.environ.get('GDAL_LIBRARY_PATH')

if os.name == 'nt':
    try:
        import osgeo

        osgeo_dir = Path(osgeo.__file__).resolve().parent
        if GEOS_LIBRARY_PATH is None:
            geos_library = osgeo_dir / 'geos_c.dll'
            if geos_library.exists():
                GEOS_LIBRARY_PATH = str(geos_library)
        if GDAL_LIBRARY_PATH is None:
            gdal_library = osgeo_dir / 'gdal.dll'
            if gdal_library.exists():
                GDAL_LIBRARY_PATH = str(gdal_library)
    except ImportError:
        pass

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',  # PostGIS support for spatial data
    # Third party
    'rest_framework',
    'corsheaders',
    # Local apps
    'apps.accounts',
    'apps.missions',
    'apps.usecases',
    'apps.agents',
    'apps.assets',
    'apps.sensors',
    'apps.telemetry',
    'apps.mapping',
    'apps.faults',
    'apps.ai_prompts',
    'apps.ai_results',
    'apps.reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

# Database Configuration
# Supports both SQLite (local development) and PostgreSQL with PostGIS (Docker/Production)
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL or RUNNING_IN_DOCKER:
    # PostgreSQL with PostGIS (Docker or Production)
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': os.environ.get('DB_NAME', 'rescuemesh'),
            'USER': os.environ.get('DB_USER', 'rescuemesh'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'rescuemesh_dev'),
            'HOST': os.environ.get('DB_HOST', 'db' if RUNNING_IN_DOCKER else 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'CONN_MAX_AGE': 600,  # Connection pooling (10 minutes)
            'OPTIONS': {
                'connect_timeout': 10,
            }
        }
    }
else:
    # SQLite (local development fallback)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (user uploads)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}

# CORS Settings for frontend
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:4321,http://127.0.0.1:4321'
).split(',')

CORS_ALLOW_CREDENTIALS = True
