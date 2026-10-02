"""Upstream test defaults with SQLite substituted; no PostgreSQL concurrency claims."""
from settings import *
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']
