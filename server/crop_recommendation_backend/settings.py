
import os
from pathlib import Path
import dj_database_url

# Load environment variables from .env file

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = True


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-c5l&#jn3ce$6*_^=@!6$4gs^9!2u^b#clktqzpzbyx)k#de842'
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-c5l&#jn3ce$6*_^=@!6$4gs^9!2u^b#clktqzpzbyx)k#de842')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1').split(',')



# Application definition


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'recommendations',
    'rest_framework',
    'corsheaders',
    'accounts',
    'rest_framework.authtoken'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://agri-smart-client.vercel.app"
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://agri-smart-client.vercel.app",
 
]
ROOT_URLCONF = 'crop_recommendation_backend.urls'

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

WSGI_APPLICATION = 'crop_recommendation_backend.wsgi.application'
CSRF_TRUSTED_ORIGINS = [f'https://{host}' for host in ALLOWED_HOSTS if host.startswith('.')]


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# database_url=os.environ.get('DATABASE_URL');
# DATABASES["default"]=dj_database_url.parse(database_url)

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
      os.path.join(BASE_DIR/'recommendation','static'),
]
# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Database configuration
# DATABASE_URL = os.environ.get('DATABASE_URL')
# if DATABASE_URL:
#     DATABASES['default'] = dj_database_url.config(
#         default=DATABASE_URL,
#         conn_max_age=600
#     )

# Serve Static Files in Development
if DEBUG:
    import mimetypes
    mimetypes.add_type("text/css", ".css", True)
    mimetypes.add_type("application/javascript", ".js", True)
    
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# JWT Authentication Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
     'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',  # Temporarily allow all requests
    ),
    
}

