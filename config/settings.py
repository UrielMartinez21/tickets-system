"""
Configuración de Django para el proyecto Sistema de Tickets de TI.

Generado para Django 5.2 LTS.
"""
from pathlib import Path

# Rutas base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# SEGURIDAD: en producción debe cargarse desde una variable de entorno.
SECRET_KEY = "django-insecure-cambiar-esta-clave-en-produccion-xk3n2m9p0q"

# SEGURIDAD: desactivar DEBUG en producción.
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


# Definición de aplicaciones
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Apps del proyecto
    "accounts",
    "tickets",
    "dashboard",
    "core",
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

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "accounts.context_processors.roles",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Base de datos: SQLite (sin configuración adicional)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "NumericPasswordValidator",
    },
]


# Internacionalización: interfaz en español (México)
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True


# Archivos estáticos (CSS, JavaScript, imágenes)
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Tipo de campo de clave primaria por defecto
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Configuración de autenticación / sesiones
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:index"
LOGOUT_REDIRECT_URL = "accounts:login"

# Duración de la sesión: expira al cerrar el navegador = False (persistente)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 60 * 60 * 8  # 8 horas
