MONGODB_USER = 'alpsApplicationUser'
MONGODB_PASSWORD = urllib.quote_plus('z(W}LSrS7/:~')
MONGODB_CONNECTION_STRING = f"mongodb://{MONGODB_USER}{MONGODB_PASSWORD}@172.16.2.59:27017/alps"
CLIENT_DB = MongoClient(MONGODB_CONNECTION_STRING).alps


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://alps-qa-new.msxguh.0001.use1.cache.amazonaws.com:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "lookup-cache": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://alps-qa-new.msxguh.0001.use1.cache.amazonaws.com:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }

    }
}

SESSION_COOKIE_SECURE = False
API_IP_ADDRESS = 'uat5.smallbizvoices.com'
ALPS_APPLICATION_SESSION_TOKEN = 'alps_st_8al32lwyk27jeg0v0fbvbylq11v1771b'

PROJECT_KW_URL_METADATA_COLLECTION = CLIENT_DB[PROJECT_KW_URL_METADATA_COLLECTION_NAME]
S3_BUCKET = 'uat.data.collection'
os.environ['DC_S3_BUCKET'] = S3_BUCKET