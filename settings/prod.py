from pymongo import MongoReplicaSetClient
from .common import *


DEBUG = False
TEMPLATE_DEBUG = False


# Only add MongoDB secondary replica server IP
MONGODB_USER = 'alpsApplicationUser'
MONGODB_PASSWORD = urllib.quote_plus('sZ$v+&x2TRhC9VSm')
MONGODB_APP_DB_NAME = 'alps'
MONGODB_REPLICA_SET = 'ReplicaSet0'
MONGODB_SERVERS = "172.31.19.255:53723,172.31.23.9:53723"
MONGODB_TAG_SETS = [{'use': 'application_read'}, {'use': 'primary'}, {}]
MONGODB_SSL_PARAMS = {
    'ssl': True,
    'ssl_certfile': "/srv/mongodb/client.pem",
    'ssl_cert_reqs': ssl.CERT_NONE,
    'ssl_ca_certs': "/srv/mongodb/ca.cert"
}

MONGODB_URI = "mongodb://%(usr)s:%(passwd)s@%(servers)s/%(db)s" % {
    'usr': MONGODB_USER, 'passwd': MONGODB_PASSWORD,
    'servers': MONGODB_SERVERS, 'db': MONGODB_APP_DB_NAME
}

# PyMongo Connection
CLIENT_DB = MongoReplicaSetClient(
    MONGODB_URI, replicaSet=MONGODB_REPLICA_SET,
    read_preference=ReadPreference.NEAREST, tag_sets=MONGODB_TAG_SETS,
    **MONGODB_SSL_PARAMS
).alps

CLIENT_DB.write_concern = {'w': 2}
CLIENT_DB.secondary_acceptable_latency_ms = 50

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://alps-production.msxguh.0001.use1.cache.amazonaws.com:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "lookup-cache": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://prod-lkup-cahe.msxguh.0001.use1.cache.amazonaws.com:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}



SESSION_COOKIE_SECURE = True
API_IP_ADDRESS = 'alpsapi.iquanti.com'
ALPS_APPLICATION_SESSION_TOKEN = 'alps_st_9c6bfk91my1dmypjhnrtk1kxb3ito8f7'

PROJECT_KW_URL_METADATA_COLLECTION = CLIENT_DB[PROJECT_KW_URL_METADATA_COLLECTION_NAME]
S3_BUCKET = 'prod.data.collection'
os.environ['DC_S3_BUCKET'] = S3_BUCKET