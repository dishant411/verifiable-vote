"""Loopback-only synthetic demo; not a deployment configuration."""
from settings import *
from pathlib import Path
import os

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']
URL_HOST = 'http://localhost:8000'
SECURE_URL_HOST = URL_HOST
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.environ.get('DEMO_DB', str(Path(__file__).resolve().parents[1] / '.runtime/demo.sqlite3'))}}
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'
AUTH_ENABLED_SYSTEMS = ['devlogin', 'password']
AUTH_DEFAULT_SYSTEM = 'devlogin'
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
DEFAULT_FROM_EMAIL = 'demo@example.invalid'
HELP_EMAIL_ADDRESS = 'demo@example.invalid'
ROLLBAR_ACCESS_TOKEN = None
SECRET_KEY = os.environ['DEMO_SECRET_KEY']

# Local presentation layer; the pinned Helios checkout stays unchanged.
SITE_TITLE = 'Verifiable Vote'
ROOT_URLCONF = 'ui_urls'
MIDDLEWARE = ['ui_middleware.DemoPresentationMiddleware', *MIDDLEWARE]
TEMPLATES = [{**config, 'DIRS': [str(Path(__file__).parent / 'ui/templates'), *config['DIRS']]} for config in TEMPLATES]
