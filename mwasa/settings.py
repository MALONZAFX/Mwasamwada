"""
Django settings for mwasa project
"""

import os
from pathlib import Path
from decouple import config
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==================== ENVIRONMENT DETECTION ====================
def detect_environment():
    """Detect current environment with Railway priority"""
    # Running on Railway (production)
    if 'RAILWAY_ENVIRONMENT' in os.environ:
        return 'railway_production'
    
    # Running locally via Railway CLI
    if 'RAILWAY_PROJECT_ID' in os.environ:
        return 'railway_local'
    
    # Pure local development
    return 'local'

ENVIRONMENT = detect_environment()

print("=" * 50)
print(f"🚀 Environment: {ENVIRONMENT.upper()}")
print("=" * 50)

# ==================== CORE SETTINGS ====================
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', config('DJANGO_SECRET_KEY', default='django-insecure-dev-key-change-in-production'))

# Debug settings - only True for pure local dev
if ENVIRONMENT == 'local':
    DEBUG = config('DEBUG', default=True, cast=bool)
else:
    DEBUG = config('DEBUG', default=False, cast=bool)

# Host settings
if ENVIRONMENT == 'local':
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']
elif ENVIRONMENT == 'railway_local':
    ALLOWED_HOSTS = ['*']  # Allow all for Railway CLI testing
else:  # railway_production
    ALLOWED_HOSTS = [
        '.railway.app',
        'www.mwasawellbeingservices.com',
        'mwasawellbeingservices.com',
        '127.0.0.1',
        'localhost'
    ]

# ==================== SMART DATABASE CONFIGURATION ====================
def get_database_config():
    """
    Smart database configuration that works in all environments.
    Priority: DATABASE_PUBLIC_URL > DATABASE_URL > SQLite
    """
    
    # 1. FIRST PRIORITY: Public URL (works everywhere)
    DATABASE_PUBLIC_URL = os.environ.get('DATABASE_PUBLIC_URL')
    if DATABASE_PUBLIC_URL:
        print("✅ Using DATABASE_PUBLIC_URL (public connection)")
        config = dj_database_url.parse(
            DATABASE_PUBLIC_URL,
            conn_max_age=600,
            conn_health_checks=True
        )
        
        # Always require SSL for public connections
        config['OPTIONS'] = config.get('OPTIONS', {})
        config['OPTIONS']['sslmode'] = 'require'
        return config
    
    # 2. SECOND PRIORITY: Regular DATABASE_URL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        print("📡 Using DATABASE_URL")
        config = dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True
        )
        
        # Only require SSL for Railway production
        if ENVIRONMENT == 'railway_production':
            config['OPTIONS'] = config.get('OPTIONS', {})
            config['OPTIONS']['sslmode'] = 'require'
        return config
    
    # 3. FALLBACK: SQLite for local development
    print("💾 No database URL found, using SQLite")
    return {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,
        }
    }

# Apply database configuration
DATABASES = {
    'default': get_database_config()
}

# Print database connection info (masked for security)
db_engine = DATABASES['default'].get('ENGINE', '')
if 'postgresql' in db_engine:
    host = DATABASES['default'].get('HOST', 'N/A')
    port = DATABASES['default'].get('PORT', 'N/A')
    name = DATABASES['default'].get('NAME', 'N/A')
    
    # Mask hostname for security in logs
    if host and 'rlwy.net' in host:
        masked_host = '***.rlwy.net'
        print(f"🔗 PostgreSQL: {masked_host}:{port}")
    elif host and 'railway.internal' in host:
        masked_host = 'railway.internal'
        print(f"🔗 PostgreSQL (internal): {masked_host}:{port}")
    else:
        print(f"🔗 PostgreSQL: {host}:{port}")
    
    print(f"📦 Database: {name}")
else:
    print(f"📁 SQLite: {DATABASES['default'].get('NAME', 'N/A')}")

# ==================== SECURITY SETTINGS ====================
if ENVIRONMENT == 'railway_production':
    # Production security
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
    
    CSRF_TRUSTED_ORIGINS = [
        'https://*.railway.app',
        'https://mwasawellbeingservices.com',
        'https://www.mwasawellbeingservices.com'
    ]
else:
    # Development security (relaxed)
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    X_FRAME_OPTIONS = 'SAMEORIGIN'
    
    if ENVIRONMENT == 'railway_local':
        CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']
    else:  # local
        CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000', 'http://0.0.0.0:8000']

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
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Static files storage - simple for development, manifest for production
if ENVIRONMENT == 'railway_production':
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Ensure directories exist
for directory in [STATIC_ROOT, MEDIA_ROOT]:
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)

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
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
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
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',  # Reduce SQL log noise
            'propagate': False,
        },
    },
}

# ==================== FINAL STARTUP MESSAGE ====================
print("=" * 50)
print(f"✅ Settings loaded successfully")
print(f"🌍 Environment: {ENVIRONMENT}")
print(f"🔧 Debug: {'ON' if DEBUG else 'OFF'}")
print(f"📊 Database: {'PostgreSQL' if 'postgresql' in str(DATABASES['default'].get('ENGINE', '')) else 'SQLite'}")
print(f"🌐 Allowed Hosts: {', '.join(ALLOWED_HOSTS[:3])}{'...' if len(ALLOWED_HOSTS) > 3 else ''}")
print("=" * 50)