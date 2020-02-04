from .common import *

DEBUG = False

# Server Connections
CLIENT_DB = MongoClient(
    "mongodb://alpsApplicationUser:%s@54.175.129.138:27017/alps" % urllib.parse.quote_plus(
        'z(W}LSrS7/:~')).alps

CACHES = {
    'default': {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://alps-qa.msxguh.0001.use1.cache.amazonaws.com:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    'lookup-cache': {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://alps-qa.msxguh.0001.use1.cache.amazonaws.com:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

SESSION_COOKIE_SECURE = False
API_IP_ADDRESS = 'alpsqaapi.smallbizvoices.com'
API_IP_PORT = '8000'
ALPS_APPLICATION_SESSION_TOKEN = 'alps_st_6xplco32vfkq5kbumjzfaveho7n0joi4'

PROJECT_KW_URL_METADATA_COLLECTION = CLIENT_DB[PROJECT_KW_URL_METADATA_COLLECTION_NAME]
S3_BUCKET = 'qa.data.collection'
os.environ['DC_S3_BUCKET'] = S3_BUCKET