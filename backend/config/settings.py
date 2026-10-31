# import os
# from datetime import timedelta
# from pathlib import Path

# from dotenv import load_dotenv

# BASE_DIR = Path(__file__).resolve().parent.parent
# load_dotenv(BASE_DIR / ".env")

# SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-change-me")
# DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() == "true"
# ALLOWED_HOSTS = [x.strip() for x in os.getenv(
#     "DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost"
# ).split(",") if x.strip()]

# INSTALLED_APPS = [
#     "django.contrib.admin",
#     "django.contrib.auth",
#     "django.contrib.contenttypes",
#     "django.contrib.sessions",
#     "django.contrib.messages",
#     "django.contrib.staticfiles",
#     "rest_framework",
#     "rest_framework_simplejwt.token_blacklist",
#     "corsheaders",
#     "api",
# ]

# MIDDLEWARE = [
#     "django.middleware.security.SecurityMiddleware",
#     "corsheaders.middleware.CorsMiddleware",
#     "django.contrib.sessions.middleware.SessionMiddleware",
#     "django.middleware.common.CommonMiddleware",
#     "django.middleware.csrf.CsrfViewMiddleware",
#     "django.contrib.auth.middleware.AuthenticationMiddleware",
#     "django.contrib.messages.middleware.MessageMiddleware",
#     "django.middleware.clickjacking.XFrameOptionsMiddleware",
# ]

# ROOT_URLCONF = "config.urls"
# TEMPLATES = [{
#     "BACKEND": "django.template.backends.django.DjangoTemplates",
#     "DIRS": [],
#     "APP_DIRS": True,
#     "OPTIONS": {"context_processors": [
#         "django.template.context_processors.debug",
#         "django.template.context_processors.request",
#         "django.contrib.auth.context_processors.auth",
#         "django.contrib.messages.context_processors.messages",
#     ]},
# }]
# WSGI_APPLICATION = "config.wsgi.application"

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.getenv("DB_NAME", "moodify"),
#         "USER": os.getenv("DB_USER", "moodify"),
#         "PASSWORD": os.getenv("DB_PASSWORD", "moodify"),
#         "HOST": os.getenv("DB_HOST", "127.0.0.1"),
#         "PORT": os.getenv("DB_PORT", "5432"),
#         "CONN_MAX_AGE": 60,
#     }
# }

# AUTH_PASSWORD_VALIDATORS = [
#     {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
#     {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
#     {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
#     {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
# ]

# LANGUAGE_CODE = "en-us"
# TIME_ZONE = "Asia/Kolkata"
# USE_I18N = True
# USE_TZ = True

# STATIC_URL = "static/"
# STATIC_ROOT = BASE_DIR / "staticfiles"
# DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS_ALLOWED_ORIGINS = [
#     x.strip() for x in os.getenv(
#         "CORS_ALLOWED_ORIGINS",
#         "http://localhost:5173,http://127.0.0.1:5173",
#     ).split(",") if x.strip()
# ]

# REST_FRAMEWORK = {
#     "DEFAULT_AUTHENTICATION_CLASSES": (
#         "rest_framework_simplejwt.authentication.JWTAuthentication",
#     ),
#     "DEFAULT_PERMISSION_CLASSES": (
#         "rest_framework.permissions.IsAuthenticated",
#     ),
#     "DEFAULT_RENDERER_CLASSES": (
#         "rest_framework.renderers.JSONRenderer",
#     ),
#     "DEFAULT_THROTTLE_RATES": {"ai": os.getenv("AI_RATE_LIMIT", "60/min"), "playback": "240/min"},
# }

# # Optional: set ANTHROPIC_API_KEY to let Claude read moods. Leave empty to use the built-in analyzer.
# ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
# ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5")
# ANTHROPIC_TIMEOUT = float(os.getenv("ANTHROPIC_TIMEOUT", "8"))

# SIMPLE_JWT = {
#     "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
#     "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
#     "ROTATE_REFRESH_TOKENS": True,
#     "BLACKLIST_AFTER_ROTATION": True,
# }

# # YouTube Data API v3 key: finds embeddable videos for full-song playback.
# YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "").strip()


# # Optional Spotify Web API credentials (track metadata/search; Spotify does not provide
# # unrestricted full-song audio through this API).
# SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "").strip()
# SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "").strip()



# import os
# from datetime import timedelta
# from pathlib import Path

# from dotenv import load_dotenv

# BASE_DIR = Path(__file__).resolve().parent.parent
# load_dotenv(BASE_DIR / ".env")

# SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-change-me")

# # DEBUG configuration
# DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"

# # Allowed hosts (Local + Render)
# ALLOWED_HOSTS = [
#     x.strip() for x in os.getenv(
#         "DJANGO_ALLOWED_HOSTS",
#         "127.0.0.1,localhost,moodify-backend-ccgx.onrender.com"
#     ).split(",") if x.strip()
# ]

# # CSRF trusted origins
# CSRF_TRUSTED_ORIGINS = [
#     x.strip() for x in os.getenv(
#         "DJANGO_CSRF_TRUSTED_ORIGINS",
#         "http://localhost:5173,http://127.0.0.1:5173,https://moodify-backend-ccgx.onrender.com"
#     ).split(",") if x.strip()
# ]

# INSTALLED_APPS = [
#     "django.contrib.admin",
#     "django.contrib.auth",
#     "django.contrib.contenttypes",
#     "django.contrib.sessions",
#     "django.contrib.messages",
#     "django.contrib.staticfiles",
#     # "rest_framework",
#     # "rest_framework_simplejwt.token_blacklist",
#     # "corsheaders",
#     # "api",
# ]

# MIDDLEWARE = [
#     "django.middleware.security.SecurityMiddleware",
#     "corsheaders.middleware.CorsMiddleware",
#     "django.contrib.sessions.middleware.SessionMiddleware",
#     "django.middleware.common.CommonMiddleware",
#     "django.middleware.csrf.CsrfViewMiddleware",
#     "django.contrib.auth.middleware.AuthenticationMiddleware",
#     "django.contrib.messages.middleware.MessageMiddleware",
#     "django.middleware.clickjacking.XFrameOptionsMiddleware",
# ]

# ROOT_URLCONF = "config.urls"

# TEMPLATES = [{
#     "BACKEND": "django.template.backends.django.DjangoTemplates",
#     "DIRS": [],
#     "APP_DIRS": True,
#     "OPTIONS": {"context_processors": [
#         "django.template.context_processors.debug",
#         "django.template.context_processors.request",
#         "django.contrib.auth.context_processors.auth",
#         "django.contrib.messages.context_processors.messages",
#     ]},
# }]

# WSGI_APPLICATION = "config.wsgi.application"

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.getenv("DB_NAME", "moodify"),
#         "USER": os.getenv("DB_USER", "moodify"),
#         "PASSWORD": os.getenv("DB_PASSWORD", "moodify"),
#         "HOST": os.getenv("DB_HOST", "127.0.0.1"),
#         "PORT": os.getenv("DB_PORT", "5432"),
#         "CONN_MAX_AGE": 60,
#     }
# }

# AUTH_PASSWORD_VALIDATORS = [
#     {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
#     {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
#     {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
#     {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
# ]

# LANGUAGE_CODE = "en-us"
# TIME_ZONE = "Asia/Kolkata"
# USE_I18N = True
# USE_TZ = True

# STATIC_URL = "static/"
# STATIC_ROOT = BASE_DIR / "staticfiles"
# DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS_ALLOWED_ORIGINS = [
#     x.strip() for x in os.getenv(
#         "CORS_ALLOWED_ORIGINS",
#         "http://localhost:5173,http://127.0.0.1:5173",
#     ).split(",") if x.strip()
# ]

# REST_FRAMEWORK = {
#     "DEFAULT_AUTHENTICATION_CLASSES": (
#         "rest_framework_simplejwt.authentication.JWTAuthentication",
#     ),
#     "DEFAULT_PERMISSION_CLASSES": (
#         "rest_framework.permissions.IsAuthenticated",
#     ),
#     "DEFAULT_RENDERER_CLASSES": (
#         "rest_framework.renderers.JSONRenderer",
#     ),
#     "DEFAULT_THROTTLE_RATES": {
#         "ai": os.getenv("AI_RATE_LIMIT", "60/min"),
#         "playback": "240/min"
#     },
# }

# # Optional: set ANTHROPIC_API_KEY to let Claude read moods.
# # Leave empty to use the built-in analyzer.
# ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
# ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5")
# ANTHROPIC_TIMEOUT = float(os.getenv("ANTHROPIC_TIMEOUT", "8"))

# SIMPLE_JWT = {
#     "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
#     "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
#     "ROTATE_REFRESH_TOKENS": True,
#     "BLACKLIST_AFTER_ROTATION": True,
# }

# # YouTube Data API v3 key
# YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "").strip()

# # Optional Spotify Web API credentials
# # Spotify provides track metadata/search, not unrestricted full-song audio.
# SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "").strip()
# SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "").strip()




import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv


# ==========================================================
# BASE CONFIGURATION
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "dev-only-change-me"
)

# Enable DEBUG by default for local development.
# Set DJANGO_DEBUG=False in production (.env on Render).
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() == "true"


# ==========================================================
# ALLOWED HOSTS
# ==========================================================

ALLOWED_HOSTS = [
    x.strip()
    for x in os.getenv(
        "DJANGO_ALLOWED_HOSTS",
        "127.0.0.1,localhost,moodify-backend-ccgx.onrender.com"
    ).split(",")
    if x.strip()
]


# ==========================================================
# CSRF TRUSTED ORIGINS
# ==========================================================

CSRF_TRUSTED_ORIGINS = [
    x.strip()
    for x in os.getenv(
        "DJANGO_CSRF_TRUSTED_ORIGINS",
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "https://moodify-backend-ccgx.onrender.com"
    ).split(",")
    if x.strip()
]


# ==========================================================
# INSTALLED APPLICATIONS
# ==========================================================

INSTALLED_APPS = [
    # Django built-in applications
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party applications
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",

    # Moodify application
    "api",
]


# ==========================================================
# MIDDLEWARE
# ==========================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    "corsheaders.middleware.CorsMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ==========================================================
# URL CONFIGURATION
# ==========================================================

ROOT_URLCONF = "config.urls"


# ==========================================================
# TEMPLATES
# ==========================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",

                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


# ==========================================================
# DATABASE - POSTGRESQL
# ==========================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",

        "NAME": os.getenv("DB_NAME", "moodify"),

        "USER": os.getenv("DB_USER", "moodify"),

        "PASSWORD": os.getenv("DB_PASSWORD", "moodify"),

        "HOST": os.getenv("DB_HOST", "127.0.0.1"),

        "PORT": os.getenv("DB_PORT", "5432"),

        "CONN_MAX_AGE": 60,
    }
}


# ==========================================================
# PASSWORD VALIDATION
# ==========================================================

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


# ==========================================================
# LANGUAGE AND TIMEZONE
# ==========================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# ==========================================================
# STATIC FILES - DJANGO ADMIN CSS AND JAVASCRIPT
# ==========================================================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

# Django automatically discovers static files from installed apps.
# No custom admin theme is required.


# ==========================================================
# MEDIA FILES
# ==========================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ==========================================================
# DEFAULT PRIMARY KEY
# ==========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ==========================================================
# CORS CONFIGURATION
# ==========================================================

CORS_ALLOWED_ORIGINS = [
    x.strip()
    for x in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if x.strip()
]


# ==========================================================
# DJANGO REST FRAMEWORK
# ==========================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),

    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),

    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),

    "DEFAULT_THROTTLE_RATES": {
        "ai": os.getenv("AI_RATE_LIMIT", "60/min"),

        "playback": "240/min",
    },
}


# ==========================================================
# JWT CONFIGURATION
# ==========================================================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),

    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    "ROTATE_REFRESH_TOKENS": True,

    "BLACKLIST_AFTER_ROTATION": True,
}


# ==========================================================
# ANTHROPIC AI CONFIGURATION
# ==========================================================

ANTHROPIC_API_KEY = os.getenv(
    "ANTHROPIC_API_KEY", ""
).strip()

ANTHROPIC_MODEL = os.getenv(
    "ANTHROPIC_MODEL", "claude-haiku-5-5"
)

ANTHROPIC_TIMEOUT = float(
    os.getenv("ANTHROPIC_TIMEOUT", "8")
)


# ==========================================================
# YOUTUBE API CONFIGURATION
# ==========================================================

YOUTUBE_API_KEY = os.getenv(
    "YOUTUBE_API_KEY", ""
).strip()


# ==========================================================
# SPOTIFY API CONFIGURATION
# ==========================================================

SPOTIFY_CLIENT_ID = os.getenv(
    "SPOTIFY_CLIENT_ID", ""
).strip()

SPOTIFY_CLIENT_SECRET = os.getenv(
    "SPOTIFY_CLIENT_SECRET", ""
).strip()
