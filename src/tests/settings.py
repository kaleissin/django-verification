SECRET_KEY = 'fififafafofofefe'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'verification',
    'demo.projectapp',
    'tests',
]

MIDDLEWARE_CLASSES = ()

ROOT_URLCONF = 'demo.urls'
