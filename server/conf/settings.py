import os
import sys
from pathlib import Path

import environ

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent  # .../server
REPO_ROOT = BASE_DIR.parent  # repo root (D:\AIPlatform)

# Make repo root importable if you still import modules from there
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# --- Environment (.env at repo root) ---
env = environ.Env(
    DJANGO_DEBUG=(bool, True),
)
env_file = REPO_ROOT / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

# --- Core settings ---
SECRET_KEY = env("DJANGO_SECRET_KEY", default=os.getenv("FLASK_SECRET", "dev-secret"))
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

# --- Applications ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.core",
    "apps.ai",  # add "apps.experts" later when you actually create it
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "conf.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Safe even if the folder doesn't exist yet
        "DIRS": [str(REPO_ROOT / "templates")],
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

WSGI_APPLICATION = "conf.wsgi.application"

# --- Database (SQLite for now) ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR / "db.sqlite3"),
    }
}

# --- Passwords ---
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        )
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- I18N ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"  # set to 'Africa/Kigali' if you prefer
USE_I18N = True
USE_TZ = True

# --- Static files ---
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]  # points to server/static
STATIC_ROOT = str(BASE_DIR / "staticfiles")  # for collectstatic later

# --- Defaults ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- App-specific env surfaced via settings (so services can import from settings) ---
DATA_DIR = env("DATA_DIR", default=str(REPO_ROOT / "data"))

OPENAI_API_KEY = env("OPENAI_API_KEY", default="")
OPENAI_MODEL = env("OPENAI_MODEL", default="gpt-4.1-mini")
MODEL_TEMP = env.float("MODEL_TEMP", default=0.3)
MODEL_TOP_P = env.float("MODEL_TOP_P", default=1.0)
MAX_OUTPUT_TOKENS = env.int("MAX_OUTPUT_TOKENS", default=2000)
LANG = env("LANG", default="English")
TAVILY_API_KEY = env("TAVILY_API_KEY", default="")
