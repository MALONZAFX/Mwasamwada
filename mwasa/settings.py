"""
Django settings for mwasa project - Smart Database Configuration
"""

from pathlib import Path
import os
import sys
from decouple import config
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==================== ENVIRONMENT DETECTION ====================
# Check if we're on Railway (minimal check)
def is_railway():
    """Simple check for Railway environment"""
    return (
        os.environ.get('RAILWAY_ENVIRONMENT') == 'production' or
        'RAILWAY' in os.environ or
        'railway.app' in os.environ.get('ALLOWED_HOSTS', '') or
        os.environ.get('RAILWAY_STATIC_URL') is not None
    )

IS_RAILWAY = is_railway()
IS_LOCAL = not IS_RAILWAY

print("=" * 50)
print(f"🚀 {'RAILWAY PRODUCTION' if IS_RAILWAY else 'LOCAL DEVELOPMENT'}")
print("=" * 50)

# ==================== CORE SETTINGS ====================
SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', cast=lambda v: [s.strip() for s in v.split(',')])

# ==================== SMART DATABASE CONFIGURATION ====================
DATABASE_URL = config('DATABASE_URL', default=None)

def test_postgres_connection(db_url):
    """Test if PostgreSQL connection is actually working"""
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        parsed = urlparse(db_url)
        
        # Try to connect
        conn = psycopg2.connect(
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port,
            connect_timeout=3
        )
        
        # Quick test query
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        
        return True
    except Exception:
        return False

# MAIN DATABASE LOGIC - Only this section changed!
if IS_RAILWAY and DATABASE_URL:
    # On Railway with DATABASE_URL
    print(f"📡 Railway DATABASE_URL detected: {DATABASE_URL[:50]}...")
    
    # Test if PostgreSQL is actually accessible
    if test_postgres_connection(DATABASE_URL):
        # PostgreSQL is working - use it!
        DATABASES = {
            'default': dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
        print("✅ PostgreSQL: Connected successfully")
    else:
        # PostgreSQL failed - use SQLite fallback
        print("⚠️ PostgreSQL connection failed - using SQLite fallback")
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db_railway_fallback.sqlite3',
            }
        }
elif DATABASE_URL and 'postgres' in DATABASE_URL.lower():
    # Has PostgreSQL URL but not on Railway (maybe Render or other)
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    print("🌐 External PostgreSQL detected")
else:
    # Local Development or no DATABASE_URL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print("💻 Local SQLite database")

# Print database info (keeping your format)
print(f"🔗 Database: {DATABASES['default']['ENGINE']}")
print(f"📁 Database Name: {DATABASES['default'].get('NAME', 'N/A')}")

# ==================== SECURITY SETTINGS ====================
# KEEPING YOUR EXACT SECURITY SETTINGS
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
else:
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
                'django.template.context_processors.media',
            ],
            'debug': DEBUG,
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
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# FIX: Use CompressedStaticFilesStorage instead of CompressedManifestStaticFilesStorage
# This prevents the "Missing staticfiles manifest entry" error
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================== EMAIL CONFIGURATION ====================
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='mwasawellservices@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='pvmrxbdvvvnchynm')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='mwasawellservices@gmail.com')
SERVER_EMAIL = config('SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)

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
        'level': config('DJANGO_LOG_LEVEL', default='INFO'),
    },
}

# ==================== ADDITIONAL SETTINGS ====================
APPEND_SLASH = True
PREPEND_WWW = config('PREPEND_WWW', default=False, cast=bool)

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600
SESSION_SAVE_EVERY_REQUEST = False

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': BASE_DIR / 'django_cache',
    }
}

# ==================== DEVELOPMENT/PRODUCTION NOTICE ====================
if DEBUG:
    print("🎯 Running in DEVELOPMENT mode")
    print("📝 Static files: Using CompressedStaticFilesStorage (no manifest)")
else:
    print("🏢 Running in PRODUCTION mode") 
    print("📝 Static files: Using CompressedStaticFilesStorage (no manifest)")
    
print("=" * 50)