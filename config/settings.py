import os
from pathlib import Path

from settings import settings

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = settings.SECRET_KEY
DEBUG = settings.DEBUG

TELEGRAM_API_TOKEN = settings.TELEGRAM_API_TOKEN
TELEGRAM_CHAT_ID = settings.TELEGRAM_CHAT_ID

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

#  APPS
INSTALLED_APPS += [
    'webfacetg',
    'accounts',
    'post',
]

# EXTENSIONS
INSTALLED_APPS += [
    'django_extensions',
    'django_celery_beat',
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

AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = 'accounts:login'
ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 30,
        }
    },
    'psql': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': settings.DB_DATABASE_PSQL,
        'USER': settings.DB_USER_PSQL,
        'PASSWORD': settings.DB_PASSWORD_PSQL,
        'HOST': settings.DB_HOST_PSQL,
        'PORT': settings.DB_PORT_PSQL,
    }
}

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

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media/"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Получение параметров подключения к Redis из переменных окружения
REDIS_HOST = settings.REDIS_HOST or "localhost"
REDIS_PORT = settings.REDIS_PORT or 6379
REDIS_DB = settings.REDIS_DB or 0

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Moscow'

SMTP_SERVER = settings.SMTP_SERVER
PORT = settings.PORT
SENDER_EMAIL = settings.SENDER_EMAIL
PASSWORD = settings.PASSWORD
ADMIN_EMAIL = settings.ADMIN_EMAIL
SUBJECT = settings.SUBJECT
BODY = settings.BODY
TO_EMAIL = settings.TO_EMAIL
TO_EMAILS = settings.TO_EMAILS

PATH_TO_JSON_FILE = settings.PATH_TO_JSON_FILE

# LOGGING
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "file_formatter": {
            "format": "{asctime}.{msecs:03.0f} | {levelname} | {pathname} line:{lineno} | {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "console_formatter": {
            "format": "{asctime} {message}",
            "style": "{",
            "datefmt": "%H:%M:%S",
        },
    },
    "handlers": {
        "post": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "post.log",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 5,  # Сохраняем последние 5 файлов
            "formatter": "file_formatter",
        },
        "celery_tasks": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "celery_tasks.log",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 5,  # Сохраняем последние 5 файлов
            "formatter": "file_formatter",
        },
        # Обработчик для вывода в консоль
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "console_formatter",
        },
    },
    "loggers": {
        "post": {
            "handlers": ["post", "console"],
            "level": "INFO",
            "propagate": False,  # Важно! Не нужно передавать сообщения в стандартный логгер Django
        },
        "celery_tasks": {
            "handlers": ["celery_tasks", "console"],
            "level": "INFO",
            "propagate": False,  # Важно! Не нужно передавать сообщения в стандартный логгер Django
        },
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
