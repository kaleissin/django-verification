import os

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

SECRET_KEY = "af3=14eh#*qlb--zs55)e)^f32e3doc)ske1ve2oeuep7r&up6"

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '::1']

MANAGERS = ADMINS = []

SITE_ID = 1

USE_I18N = True
USE_L10N = True

TIME_ZONE = "America/Chicago"
LANGUAGE_CODE = "en-us"

# These are for user-uploaded content.
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "site_media")
MEDIA_URL = "/media/"

# These are for site static media (e.g. CSS and JS)
# This one is where static content is collected to.
STATIC_ROOT = os.path.join(PROJECT_ROOT, "static-root")
STATIC_URL = "/static/"
ADMIN_MEDIA_PREFIX = "/static/admin/"
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, "static"),
]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Template stuff

TEMPLATE_DIRS = [
    os.path.join(PROJECT_ROOT, "templates"),
]

ROOT_URLCONF = "demo.urls"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'demo.sqlite',
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}

INSTALLED_APPS = [
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.messages',

    'verification',
    'demo.projectapp',
]
