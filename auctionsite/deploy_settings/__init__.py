import dj_database_url
from ..settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = [
    get_env_variable("ALLOWED_HOST_SECRET_1"),
    get_env_variable("ALLOWED_HOST_SECRET_2"),
]

SECRET_KEY = get_env_variable("SECRET_KEY")

STATICFILES_STORAGE = "whitenoise.django.GzipManifestStaticFilesStorage"

db_from_env = dj_database_url.config()
DATABASES["default"].update(db_from_env)

# Using Email Server
DEFAULT_FROM_EMAIL = get_env_variable("EMAIL_FROM_SECRET")

SPARKPOST_API_KEY = get_env_variable("EMAIL_PASS")
EMAIL_BACKEND = 'sparkpost.django.email_backend.SparkPostEmailBackend'
SPARKPOST_OPTIONS = {
    'track_opens': False,
    'track_clicks': False,
    'transactional': True,
    "domain": "www.auctionsite.com",
}

CLOUDINARY = {
    'cloud_name': get_env_variable("CLOUDINARY_NAME_SECRET"),
    'api_key': get_env_variable("CLOUDINARY_API_KEY"),
    'api_secret': get_env_variable("CLOUDINARY_API_SECRET"),
}
