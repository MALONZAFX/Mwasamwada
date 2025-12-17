"""
Django settings for mwasa project
"""

from pathlib import Path
import os
from decouple import config
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==================== ENVIRONMENT DETECTION ====================
def detect_environment():
    """Smart environment detection"""
    # Check for Railway explicitly
    if 'RAILWAY_ENVIRONMENT' in os.environ:
        return 'railway'
    
    if 'RAILWAY_STATIC_URL' in os.environ:
        return 'railway'
    
    # Check for PORT environment variable (Railway provides this)
    if 'PORT' in os.environ:
        return 'railway'
    
    # Default to local for development
    return 'local'

ENVIRONMENT = detect_environment()

print("=" * 50)
print(f"🚀 Environment: {ENVIRONMENT.upper()}")
print("=" * 50)

# ==================== CORE SETTINGS ====================
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', config('DJANGO_SECRET_KEY', default='django-insecure-fallback-key-for-development-only'))

# Debug settings based on environment
if ENVIRONMENT == 'local':
    DEBUG = config('DEBUG', default=True, cast=bool)
else:
    DEBUG = config('DEBUG', default=False, cast=bool)

# Host settings
ALLOWED_HOSTS = ['*'] if DEBUG else config(
    'ALLOWED_HOSTS', 
    default='.railway.app,www.mwasawellbeingservices.com,mwasawellbeingservices.com',
    cast=lambda v: [s.strip() for s in v.split(',') if s.strip()]
)

CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS', 
    default='https://*.railway.app,https://www.mwasawellbeingservices.com,https://mwasawellbeingservices.com',
    cast=lambda v: [s.strip() for s in v.split(',') if s.strip()]
)

# ==================== SMART DATABASE CONFIGURATION ====================
def setup_sqlite():
    """Setup SQLite database for local development"""
    db_path = BASE_DIR / 'db.sqlite3'
    return {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': db_path,
        }
    }

def setup_postgresql(db_url):
    """Setup PostgreSQL database with proper configuration"""
    db_config = dj_database_url.parse(db_url, conn_max_age=600, conn_health_checks=True)
    
    # Add SSL requirement for production (Railway)
    if ENVIRONMENT == 'railway':
        db_config['OPTIONS'] = db_config.get('OPTIONS', {})
        db_config['OPTIONS']['sslmode'] = 'require'
    
    return {'default': db_config}

# MAIN DATABASE LOGIC
print(f"🌐 Environment: {ENVIRONMENT}")

if ENVIRONMENT == 'railway':
    # On Railway, always use PostgreSQL from DATABASE_URL environment variable
    RAILWAY_DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if RAILWAY_DATABASE_URL and RAILWAY_DATABASE_URL.startswith('postgresql://'):
        print("🚂 Railway detected - using PostgreSQL")
        DATABASES = setup_postgresql(RAILWAY_DATABASE_URL)
    else:
        print("⚠️ Warning: No DATABASE_URL found, using SQLite")
        DATABASES = setup_sqlite()
        
elif ENVIRONMENT == 'local':
    # Local development
    DATABASE_URL = config('DATABASE_URL', default='sqlite:///db.sqlite3')
    USE_POSTGRESQL_LOCAL = config('USE_POSTGRESQL_LOCAL', default=False, cast=bool)
    
    if USE_POSTGRESQL_LOCAL and DATABASE_URL.startswith('postgresql://'):
        print("💻 Local development with PostgreSQL")
        DATABASES = setup_postgresql(DATABASE_URL)
    else:
        print("💾 Local development with SQLite")
        DATABASES = setup_sqlite()

print(f"📊 Database Engine: {DATABASES['default']['ENGINE']}")

# ==================== SECURITY SETTINGS ====================
if ENVIRONMENT != 'local':
    # Production security settings
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    # Local development - relaxed security
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

X_FRAME_OPTIONS = 'DENY'

# ==================== APPLICATION DEFINITION ====================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'content',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mwasa.urls'

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

WSGI_APPLICATION = 'mwasa.wsgi.application'

# ==================== PASSWORD VALIDATION ====================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ==================== INTERNATIONALIZATION ====================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# ==================== STATIC & MEDIA FILES ====================
# IMPORTANT: Fix for Whitenoise manifest issue
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

if ENVIRONMENT == 'railway':
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    # Use CompressedManifestStaticFilesStorage only if you run collectstatic
    # Otherwise use simpler storage for development
    if DEBUG:
        STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
    else:
        STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    # Local development - simple static serving
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Ensure staticfiles directory exists
if not STATIC_ROOT.exists():
    STATIC_ROOT.mkdir(parents=True, exist_ok=True)

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Ensure media directory exists
if not MEDIA_ROOT.exists():
    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================== EMAIL CONFIGURATION ====================
if ENVIRONMENT == 'local':
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
    DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@mwasawellbeingservices.com')

# ==================== LOGGING CONFIGURATION ====================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
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
            'propagate': True,
        },
    },
}

print("=" * 50)
print(f"✅ Settings loaded successfully")
print(f"🔧 Debug: {'ON' if DEBUG else 'OFF'}")
print(f"📊 Database: {'PostgreSQL' if 'postgresql' in str(DATABASES['default'].get('ENGINE', '')) else 'SQLite'}")
print("=" * 50)