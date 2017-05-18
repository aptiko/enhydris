import os
import tempfile

# Development settings (to be overriden in production settings.py)
DEBUG = True
SECRET_KEY = 'topsecret'
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': 'enhydris.db',
    }
}
if os.path.exists('/usr/lib/x86_64-linux-gnu/mod_spatialite.so'):
    # This is necessary for spatialite>=4.2
    SPATIALITE_LIBRARY_PATH = 'mod_spatialite'
SITE_ID = 1
STATIC_URL = '/static/'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST = 'smtp.my.domain'
DEFAULT_FROM_EMAIL = 'user@host.domain'
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_HOST_USER = 'automaticsender@my.domain'
EMAIL_HOST_PASSWORD = 'mypassword'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ROOT_URLCONF = 'enhydris.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.gis',
    'django.contrib.flatpages',

    'rest_framework',

    'ajax_select',
    'captcha',
    'bootstrap3',

    'enhydris.hcore',
    'enhydris.api',
    'enhydris.permissions',

    # enhydris.hcore overrides some templates from django.contrib.admin; for
    # this reason, it must be listed in INSTALLED_APPS before
    # django.contrib.admin.
    'django.contrib.admin',
    # Registration templates it must be listed in INSTALLED_APPS after
    # 'enhydris.hcore' in order to overide django-default templates.
    'registration',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

APPEND_SLASH = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'enhydris.hcore.context_processors.registration',
                'enhydris.hcore.context_processors.map',
            ],
        },
    },
]

AUTH_PROFILE_MODULE = 'hcore.UserProfile'
LOGIN_REDIRECT_URL = '/'

ATOMIC_REQUESTS = True
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
USE_TZ = True

# Options for django-registration
ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_OPEN = True

# Options for django-ajax-selects
AJAX_LOOKUP_CHANNELS = {
    'maintainers': dict(model='auth.User', search_field='username'),
}

# Default Enhydris settings
ENHYDRIS_FILTER_DEFAULT_COUNTRY = None
ENHYDRIS_FILTER_POLITICAL_SUBDIVISION1_NAME = None
ENHYDRIS_FILTER_POLITICAL_SUBDIVISION2_NAME = None
ENHYDRIS_USERS_CAN_ADD_CONTENT = False
ENHYDRIS_SITE_CONTENT_IS_FREE = False
ENHYDRIS_TSDATA_AVAILABLE_FOR_ANONYMOUS_USERS = False
ENHYDRIS_MIN_VIEWPORT_IN_DEGS = 0.04
ENHYDRIS_MAP_DEFAULT_VIEWPORT = (19.3, 34.75, 29.65, 41.8)
ENHYDRIS_TIMESERIES_DATA_DIR = 'timeseries_data'
ENHYDRIS_TS_GRAPH_BIG_STEP_DENOMINATOR = 200
ENHYDRIS_TS_GRAPH_FINE_STEP_DENOMINATOR = 50
ENHYDRIS_SITE_STATION_FILTER = {}
ENHYDRIS_DISPLAY_COPYRIGHT_INFO = False
ENHYDRIS_WGS84_NAME = 'WGS84'
ENHYDRIS_MAP_BASE_LAYERS = [
    r'OpenLayers.Layer.OSM.Mapnik("Open Street Map",'
    r'{isBaseLayer:true,attribution:'
    r'''"Map by <a href='http://www.openstreetmap.org/'>OSM</a>"})''',

    r'OpenLayers.Layer.OSM.CycleMap("Open Cycle Map",'
    r'{isBaseLayer: true, attribution:'
    r'''"Map by <a href='http://www.openstreetmap.org/'>OSM</a>"})''',
]
ENHYDRIS_MAP_BOUNDS = ((19.3, 34.75), (29.65, 41.8))
ENHYDRIS_MAP_MARKERS = {'0': 'images/drop_marker.png'}
if os.environ.get('SELENIUM_BROWSER', False):
    from selenium import webdriver
    SELENIUM_WEBDRIVERS = {
        'default': {
            'callable': webdriver.__dict__[os.environ['SELENIUM_BROWSER']],
            'args': (),
            'kwargs': {},
        }
    }