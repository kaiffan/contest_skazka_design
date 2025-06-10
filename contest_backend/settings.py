from datetime import timedelta
from pathlib import Path

from config.settings import get_settings

settings = get_settings()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = settings.token_credentials.SECRET_KEY

DEBUG = False

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "rest_framework_simplejwt.token_blacklist",
    "rest_framework_simplejwt",
    "rest_framework",
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "age_categories",
    "applications",
    "authentication",
    "block_user",
    "competencies",
    "contest_categories",
    "file_constraints",
    "contest_criteria",
    "contest_nominations",
    "contest_stage",
    "contest_file_constraints",
    "contests",
    "contests_contest_stage",
    "criteria",
    "email_confirmation",
    "nomination",
    "participants",
    "regions",
    "storage_s3",
    "users",
    "vk_news",
    "vk_news_attachments",
    "winners",
    "work_rate",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "contests.middleware.ContestHeaderMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "contest_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "contest_backend.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": settings.postgres_credentials.DATABASE_NAME,
        "USER": settings.postgres_credentials.USERNAME,
        "PASSWORD": settings.postgres_credentials.PASSWORD,
        "HOST": settings.postgres_credentials.HOST,
        "PORT": settings.postgres_credentials.PORT
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "authentication.Users"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=6),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://admin:admin@127.0.0.1:6380/0",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = settings.email_credentials.HOST
EMAIL_PORT = settings.email_credentials.PORT
EMAIL_USE_SSL = True
EMAIL_HOST_USER = settings.email_credentials.HOST_USER
EMAIL_HOST_PASSWORD = settings.email_credentials.HOST_PASSWORD

CODE_CONFIRMATION_SALT = settings.email_credentials.CODE_CONFIRMATION_SALT

CSRF_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SAMESITE = "None"

CSRF_COOKIE_SECURE = True

SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_NAME = "email_login_session_id"
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ["accept", "content-type", "authorization", "X-Contest-Id"]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
