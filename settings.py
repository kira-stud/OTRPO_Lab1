from os import environ
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env.docker")
# load_dotenv(dotenv_path=".env.test")

SECRET_KEY = environ.get('SECRET_KEY')
REDIS_HOST = environ.get('REDIS_HOST')
REDIS_PORT = environ.get('REDIS_PORT')
REDIS_DB = environ.get('REDIS_DB')

EMAIL = environ.get('EMAIL')
EMAIL_PSW = environ.get('EMAIL_PSW')

FTP_HOST = environ.get('FTP_HOST')
FTP_USER = environ.get('FTP_USER')
FTP_PSW = environ.get('FTP_PSW')

POSTGRESQL_USER = environ.get('POSTGRESQL_USER')
POSTGRESQL_PSW = environ.get('POSTGRESQL_PSW')
POSTGRESQL_DB = environ.get('POSTGRESQL_DB')
POSTGRESQL_HOST = environ.get('POSTGRESQL_HOST')
POSTGRESQL_PORT = environ.get('POSTGRESQL_PORT')

YANDEX_CLIENT_ID = environ.get('YANDEX_CLIENT_ID')
YANDEX_CLIENT_SECRET = environ.get('YANDEX_CLIENT_SECRET')

GRAFANA_PSW = environ.get('GRAFANA_PSW')
