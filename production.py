from .base import *
import dj_database_url

DEBUG = False
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

# Activate Django-Heroku.
django_heroku.settings(locals(), staticfiles=False)

DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
             'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

INTERNAL_IPS = ('127.0.0.1',)
