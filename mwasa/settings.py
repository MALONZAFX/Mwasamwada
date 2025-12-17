"""
Django settings for mwasa project - Railway Optimized
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ==================== ENVIRONMENT DETECTION ====================
ENVIRONMENT = 'railway' if 'RAILWAY_ENVIRONMENT' in os.environ else 'local'

print("=" * 50)
print(f"🚀 Environment: {ENVIRONMENT.upper()}")
print("=" * 50)

# ==================== CORE SETTINGS ====================
# FIXED: Safe environment variable access with fallbacks
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

if not SECRET_KEY:
    if ENVIRONMENT == 'railway':
        print("⚠️  WARNING: DJANGO_SECRET_KEY not set on Railway!")
        print("   Using generated fallback key (ADD DJANGO_SECRET_KEY TO RAILWAY VARIABLES)")
        # Generate a deterministic fallback for Railway
        import hashlib
        fallback_seed = os.environ.get('DATABASE_URL', 'railway-fallback') + os.environ.get('RAILWAY_GIT_COMMIT_SHA', '')
        SECRET_KEY = hashlib.sha256(fallback_seed.encode()).hexdigest()
    else:
        SECRET_KEY = 'django-insecure-dev-key-for-local-development-only-2024'
        print("⚠️  Using development secret key for local testing")

DEBUG_STR = os.environ.get('DEBUG', '').lower()
DEBUG = DEBUG_STR == 'true'

# Parse ALLOWED_HOSTS from environment with fallbacks
ALLOWED_HOSTS_STR = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',') if host.strip()]

if not ALLOWED_HOSTS:
    if ENVIRONMENT == 'railway':
        # Default Railway hosts
        ALLOWED_HOSTS = ['.railway.app', '.up.railway.app']
        print("⚠️  No ALLOWED_HOSTS set, using Railway defaults")
    else:
        ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']
        print("⚠️  No ALLOWED_HOSTS set, using local defaults")

# Parse CSRF_TRUSTED_ORIGINS from environment with fallbacks
CSRF_TRUSTED_ORIGINS_STR = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS_STR.split(',') if origin.strip()]

if not CSRF_TRUSTED_ORIGINS and ENVIRONMENT == 'railway':
    CSRF_TRUSTED_ORIGINS = ['https://*.railway.app', 'https://*.up.railway.app']

# ==================== DATABASE CONFIGURATION ====================
def parse_postgres_url(db_url):
    """Parse PostgreSQL URL from Railway"""
    from urllib.parse import urlparse
    
    try:
        parsed = urlparse(db_url)
        
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': parsed.path[1:],  # Remove leading slash
            'USER': parsed.username,
            'PASSWORD': parsed.password,
            'HOST': parsed.hostname,
            'PORT': parsed.port or 5432,
            'CONN_MAX_AGE': 600,
            'OPTIONS': {
                'sslmode': 'require',
            }
        }
    except Exception as e:
        print(f"❌ Error parsing database URL: {e}")
        # Fallback to SQLite
        return {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }

# Use DATABASE_URL from Railway (it's already the public one)
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
    print(f"✅ Using DATABASE_URL from Railway")
    DATABASES = {'default': parse_postgres_url(DATABASE_URL)}
    
    # Print connection info (masked)
    db_config = DATABASES['default']
    host = db_config.get('HOST', '')
    if 'rlwy.net' in host:
        masked_host = f"{host.split('.')[0]}.***.rlwy.net"
        print(f"🔗 PostgreSQL: {masked_host}:{db_config.get('PORT', '')}")
    else:
        print(f"🔗 PostgreSQL: {host}:{db_config.get('PORT', '')}")
else:
    # Fallback to SQLite
    print("💾 Using SQLite (no DATABASE_URL found)")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ==================== SECURITY SETTINGS ====================
if ENVIRONMENT == 'railway':
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    X_FRAME_OPTIONS = 'SAMEORIGIN'

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
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
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
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================== EMAIL CONFIGURATION ====================
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = os.environ.get('EMAIL_PORT', '587')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@mwasawellbeingservices.com')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', DEFAULT_FROM_EMAIL)

# ==================== LOGGING ====================
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
        'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
    },
}

# ==================== FINAL STARTUP MESSAGE ====================
print("=" * 50)
print(f"✅ Settings loaded successfully")
print(f"🌍 Environment: {ENVIRONMENT}")
print(f"🔧 Debug: {'ON' if DEBUG else 'OFF'}")
print(f"🔑 Secret Key: {'✓ SET' if SECRET_KEY and SECRET_KEY.startswith('django-insecure') else '✓ GENERATED' if SECRET_KEY else '✗ MISSING'}")
print(f"📊 Database: {'PostgreSQL' if DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql' else 'SQLite'}")
print(f"📧 Email: {EMAIL_BACKEND}")
print(f"🌐 Allowed Hosts: {len(ALLOWED_HOSTS)} hosts configured")
print("=" * 50)