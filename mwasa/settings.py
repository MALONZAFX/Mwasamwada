"""
Django settings for mwasa project - Smart Database Configuration
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
    railway_env_vars = [
        'RAILWAY_ENVIRONMENT',
        'RAILWAY_STATIC_URL',
        'RAILWAY_DEPLOYMENT_ID',
        'RAILWAY_PROJECT_NAME',
        'RAILWAY_GIT_COMMIT_SHA',
        'RAILWAY_GIT_BRANCH'
    ]
    
    # Check for any Railway environment variable
    if any(os.environ.get(var) for var in railway_env_vars):
        return 'railway'
    
    # Check for PORT environment variable (Railway always sets this)
    if 'PORT' in os.environ and 'GIT_REV' in os.environ:
        return 'railway'
    
    # Check if running in Railway's internal network
    if 'RAILWAY' in os.environ.get('HOSTNAME', '').upper():
        return 'railway'
    
    # Check DATABASE_URL for Railway pattern
    db_url = os.environ.get('DATABASE_URL', '')
    if 'railway' in db_url or '.rlwy.net' in db_url:
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
DEFAULT_ALLOWED_HOSTS = '127.0.0.1,localhost'
if ENVIRONMENT == 'railway':
    DEFAULT_ALLOWED_HOSTS += ',*.railway.app'

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=DEFAULT_ALLOWED_HOSTS, cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])

# CSRF settings
DEFAULT_CSRF_TRUSTED_ORIGINS = 'http://127.0.0.1:8000,http://localhost:8000'
if ENVIRONMENT == 'railway':
    DEFAULT_CSRF_TRUSTED_ORIGINS += ',https://*.railway.app'

CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default=DEFAULT_CSRF_TRUSTED_ORIGINS, cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])

# ==================== SMART DATABASE CONFIGURATION ====================
def setup_sqlite():
    """Setup SQLite database for local development"""
    db_path = BASE_DIR / 'db.sqlite3'
    return {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': db_path,
            'OPTIONS': {
                'timeout': 20,
            }
        }
    }

def setup_postgresql(db_url):
    """Setup PostgreSQL database with proper configuration"""
    # Parse the database URL
    db_config = dj_database_url.parse(db_url, conn_max_age=600, conn_health_checks=True)
    
    # Add SSL requirement for production (Railway)
    if ENVIRONMENT == 'railway':
        db_config['OPTIONS'] = db_config.get('OPTIONS', {})
        db_config['OPTIONS']['sslmode'] = 'require'
    
    return {'default': db_config}

def test_postgres_connection(db_url, timeout=5):
    """Test PostgreSQL connection (for local debugging only)"""
    try:
        import psycopg2
        from urllib.parse import urlparse
        import time
        
        print(f"🔍 Testing PostgreSQL connection...")
        parsed = urlparse(db_url)
        
        db_params = {
            'database': parsed.path[1:],
            'user': parsed.username,
            'password': parsed.password,
            'host': parsed.hostname,
            'port': parsed.port,
            'connect_timeout': timeout
        }
        
        print(f"   Host: {db_params.get('host', 'N/A')}:{db_params.get('port', 'N/A')}")
        print(f"   Database: {db_params.get('database', 'N/A')}")
        
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute("SELECT version(), current_database(), current_user")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        elapsed = time.time() - start_time
        print(f"✅ PostgreSQL: Connected in {elapsed:.2f}s")
        print(f"   PostgreSQL Version: {result[0].split(',')[0]}")
        print(f"   Current DB: {result[1]}")
        print(f"   Current User: {result[2]}")
        
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

# MAIN DATABASE LOGIC
print(f"🌐 Environment: {ENVIRONMENT}")
print(f"🔧 Debug Mode: {'ON' if DEBUG else 'OFF'}")

if ENVIRONMENT == 'railway':
    # On Railway, always use PostgreSQL from DATABASE_URL environment variable
    RAILWAY_DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if RAILWAY_DATABASE_URL and RAILWAY_DATABASE_URL.startswith('postgresql://'):
        print("🚂 Railway detected - using PostgreSQL from DATABASE_URL")
        DATABASES = setup_postgresql(RAILWAY_DATABASE_URL)
    else:
        # Fallback - this shouldn't happen on Railway but just in case
        print("⚠️ Warning: No DATABASE_URL found on Railway, using SQLite fallback")
        DATABASES = setup_sqlite()
        
elif ENVIRONMENT == 'local':
    # Local development - user choice between SQLite and PostgreSQL
    DATABASE_URL = config('DATABASE_URL', default='sqlite:///db.sqlite3')
    USE_POSTGRESQL_LOCAL = config('USE_POSTGRESQL_LOCAL', default=False, cast=bool)
    
    if USE_POSTGRESQL_LOCAL and DATABASE_URL.startswith('postgresql://'):
        print("💻 Local development with PostgreSQL")
        
        # Test connection first
        try:
            import psycopg2
            # If we can import psycopg2, try to use PostgreSQL
            DATABASES = setup_postgresql(DATABASE_URL)
            print("✅ Using PostgreSQL for local development")
        except ImportError:
            print("❌ psycopg2 not installed, falling back to SQLite")
            print("💡 Install with: pip install psycopg2-binary")
            DATABASES = setup_sqlite()
    else:
        print("💾 Local development with SQLite")
        DATABASES = setup_sqlite()

# Print final database info
print(f"📊 Database Engine: {DATABASES['default']['ENGINE']}")
if DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
    print(f"📁 SQLite Path: {DATABASES['default']['NAME']}")
else:
    db_info = DATABASES['default']
    host = db_info.get('HOST', 'N/A')
    port = db_info.get('PORT', 'N/A')
    # Mask host for security in logs
    if host != 'N/A' and 'rlwy.net' in host:
        masked_host = host.split('.')[0] + '.***.rlwy.net'
        print(f"🌐 PostgreSQL: {masked_host}:{port}")
    else:
        print(f"🌐 PostgreSQL: {host}:{port}")
    print(f"📦 Database: {db_info.get('NAME', 'N/A')}")

# ==================== SECURITY SETTINGS ====================
if ENVIRONMENT != 'local':
    # Production security settings
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
else:
    # Local development - relaxed security
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0

X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'same-origin'

# ==================== APPLICATION DEFINITION ====================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',  # Disable Django static for Whitenoise
    'content',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Must be after SecurityMiddleware
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

# Whitenoise configuration
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Keep this for Django < 4.2 compatibility
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

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
    SERVER_EMAIL = config('SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)

# ==================== LOGGING CONFIGURATION ====================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'django.log',
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
            'level': config('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': True,
        },
        'django.db.backends': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# ==================== ADDITIONAL SETTINGS ====================
APPEND_SLASH = True
PREPEND_WWW = config('PREPEND_WWW', default=False, cast=bool)

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_SAVE_EVERY_REQUEST = False

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# File upload settings
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

# Authentication URLs
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ==================== FINAL STARTUP MESSAGE ====================
print("=" * 50)
print(f"✅ Settings loaded successfully")
print(f"🌍 Environment: {ENVIRONMENT.upper()}")
print(f"🔧 Debug: {'ON' if DEBUG else 'OFF'}")
print(f"📊 Database: {'PostgreSQL' if 'postgresql' in str(DATABASES['default'].get('ENGINE', '')) else 'SQLite'}")
print(f"🌐 Allowed Hosts: {', '.join(ALLOWED_HOSTS[:3])}{'...' if len(ALLOWED_HOSTS) > 3 else ''}")
print("=" * 50)