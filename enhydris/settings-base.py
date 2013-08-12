import os
import tempfile

USE_I18N = True
LOCALE_PATHS = (os.path.join(ENHYDRIS_PROGRAM_DIR, 'locale'),)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django_notify.middleware.NotificationsMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'enhydris.sorting.middleware.SortingMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'enhydris.urls'
APPEND_SLASH = True

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django_notify.context_processors.notifications',
)

TEMPLATE_DIRS = (os.path.join(ENHYDRIS_PROGRAM_DIR, 'templates'),)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.markup',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.gis',

    'django_extensions',
    'rest_framework',
    'south',
    'pagination',
    'enhydris.sorting',
    'registration',
    'ajax_select',

    'enhydris.dbsync',
    'enhydris.hcore',
    'enhydris.api',
    'enhydris.permissions',
)

NOTIFICATIONS_STORAGE = 'session.SessionStorage'

AJAX_LOOKUP_CHANNELS = {
    'maintainers': dict(model='auth.User', search_field='username'),
}

LOGIN_REDIRECT_URL = '/'
AUTH_PROFILE_MODULE = 'hcore.UserProfile'
USE_OPEN_LAYERS = True
MIN_VIEWPORT_IN_DEGS = 0.04

HRAIN_IGNORE_ONGOING_EVENT = False

SITE_STATION_FILTER = {}

PAGINATION_INVALID_PAGE_RAISES_404 = True

TS_GRAPH_BIG_STEP_DENOMINATOR=200
TS_GRAPH_FINE_STEP_DENOMINATOR=50
TS_GRAPH_CACHE_DIR = os.path.join(tempfile.gettempdir(),
                                                'enhydris-timeseries-graphs')
TSDATA_AVAILABLE_FOR_ANONYMOUS_USERS = False
DISPLAY_COPYRIGHT_INFO = False
USERS_CAN_ADD_CONTENT = False