# Development Environment Configuration Files
"""
Django settings for lemon_mall project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os,sys
from pathlib import Path
import certifi, os

os.environ['SSL_CERT_FILE'] = certifi.where()
# View package path
# print(sys.path)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
IP_ADDRESS = '192.168.112.134'
# Append the package guide path to the apps package
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-)szxdt#$e6j^sp@xeh!=2@09tnie)dzo19$-p8qbjyolztv215'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '192.168.1.14',
    '127.0.0.1'
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'haystack', # Full text search

    'users',  # User module
    'contents',  # Home Advertising module
    'verifications',  # CAPTCHA
    'oauth',  # Third Party Login
    'areas',  # Provincial, municipal and district level
    'goods',  # Goods
    'carts',  # Shopping cart
    'orders', # Order
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lemon_mall.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2', # Configure the jinja2 template engine
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Configure the path for loading template files
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # Supplementary Jinja2 template engine environment
            'environment': 'lemon_mall.utils.jinja2_env.jinja2_environment',
        },
    },
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

WSGI_APPLICATION = 'lemon_mall.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': IP_ADDRESS,
        'PORT': 3306,
        'USER': 'alex',
        'PASSWORD': '123456abcdefg',
        'NAME': 'lemonmall'
    },
}

# Configure the Redis Database
CACHES = {
    "default": { # default
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{IP_ADDRESS}:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": { # session
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{IP_ADDRESS}:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "verify_code": { # captcha
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{IP_ADDRESS}:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "history": { # User Browsing History
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{IP_ADDRESS}:6379/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "carts": { # Cart
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{IP_ADDRESS}:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"
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
# Specify the route prefix for loading static files
STATIC_URL = 'static/'
# Configure static file loading path
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configure the project log
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # Whether to disable an existing logger
    'formatters': {  # Format of log message display
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # Filtering of logs
        'require_debug_true': {  # django outputs logs only in debug mode
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # Log Handling Methods
        'console': {  # Output logs to the terminal
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # Output logs to a file
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/lemonmall.log'),  # Location of log files
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {  # Defines a logger named django
            'handlers': ['console', 'file'],  # Can output logs to the terminal and to a file at the same time
            'propagate': True,  # Whether to continue passing log messages
            'level': 'INFO',  # Minimum log level received by the logger
        },
    }
}

# Specify custom user model classes: Syntax: subapplication.User Model Classes
AUTH_USER_MODEL = 'users.User'

# Specify the backend for custom user authentication
AUTHENTICATION_BACKENDS = ['users.utils.UsernameMobileBackend']

# After determining whether a user is logged in or not, specify the address to which non-logged-in users are redirected
LOGIN_URL = '/login/'

# Configuration file for QQ login
QQ_CLIENT_ID = ''
QQ_CLIENT_SECRET = ''
QQ_REDIRECT_URI = ''

# Mail Parameters
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # Specify mail backend
EMAIL_HOST = 'smtp.gmail.com' # Email Hosting
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'sgsgkxkx@gmail.com' # Authorized mailboxes
EMAIL_HOST_PASSWORD = '' # Password obtained during mailbox authorization, not the registered login password
EMAIL_FROM = 'LemonMall<sgsgkxkx@gmail.com>' # Sender's letterhead

# Email verification link
EMAIL_VERIFY_URL = 'http://192.168.1.14:8000/emails/verification/'

# DEFAULT_FILE_STORAGE = 'lemon_mall.utils.fastdfs.fdfs_storage.FastDFSStorage'
# Specify a custom Django file storage class
STORAGES = {
    "default": {
        "BACKEND": 'lemon_mall.utils.fastdfs.fdfs_storage.FastDFSStorage',
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# FastDFS related parameters
FDFS_BASE_URL = 'http://192.168.112.134:8888/'

# Haystack
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://192.168.112.134:9200/', # Elasticsearch server ip address, port number fixed to 9200
        'INDEX_NAME': 'lemon_mall', # Name of the index repository created by Elasticsearch
    },
}

# Automatic index generation when adding, modifying, or deleting data
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# Number of records per page for haystack paging
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 5
