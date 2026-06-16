
import os
from pathlib import Path
from dotenv import load_dotenv


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Load environment variables from the .env file
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
# Raises an error if SECRET_KEY is not found in the environment
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
# Evaluates to True if the string is 'True', '1', or 't'
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

# Parses the comma-separated string from .env into a Python list
allowed_hosts_env = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost')
ALLOWED_HOSTS = allowed_hosts_env.split(',')

# Application definition

INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'API',

]

UNFOLD = {
    "SITE_TITLE": "Portfolio Admin",
    "SITE_HEADER": "Admin Dashboard",
    "SITE_URL": "/",
    
    # Enables a toggle in the UI allowing users to switch between Light and Dark mode
    "DARK_MODE": True, 
    
    # Custom Blue Color Palette (Uses Tailwind-compatible space-separated RGB values)
    "COLORS": {
        "primary": {
            "50": "239 246 255",   # blue-50
            "100": "219 234 254",  # blue-100
            "200": "191 219 254",  # blue-200
            "300": "147 197 253",  # blue-300
            "400": "96 165 250",   # blue-400
            "500": "59 130 246",   # blue-500 (Base Primary)
            "600": "37 99 235",    # blue-600
            "700": "29 78 216",    # blue-700
            "800": "30 64 175",    # blue-800
            "900": "30 58 138",    # blue-900
            "950": "23 37 84",     # blue-950
        },
    },
    
    # Optional Sidebar Config
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "API.middleware.VisitorTrackingMiddleware",
    "API.middleware.DomainRouter",
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / "Template"] ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

# 1. The URL users/browsers use to access static files
STATIC_URL = 'Static/'

# 2. Where Django looks for static files during local development
STATICFILES_DIRS = [
    BASE_DIR / "Static", 
]

# 3. Where Django WILL DUMP all static files when preparing for production
STATIC_ROOT = BASE_DIR / "staticfiles"

# Base url to serve media files
MEDIA_URL = 'media/'

STATICFILES_STORAGE = "whitenoise.strorage.CompressedMainfestStaticFilesStorage"

# Path where media is stored
MEDIA_ROOT = BASE_DIR / 'media'
