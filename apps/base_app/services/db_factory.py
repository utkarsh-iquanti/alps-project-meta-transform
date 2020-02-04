import datetime
import time

from collections import OrderedDict
from pymongo.errors import BulkWriteError

# import logging
# error_logger = logging.getLogger('error.transform.keyword')

# def log_error(tenant_code, project_id, keyword, url, tag, msg):
#     error_logger.error('Project Transform|%s|%s|%s|%s|%s|%s' % (
#         tenant_code, project_id, keyword, url, tag, msg
#     ))


def get_ordered_query(query):
    return OrderedDict([
        ('tenant_code', query['tenant_code']),
        ('project_id', query['project_id']),
        ('_tag', query['_tag']),
        ('keyword', query['keyword']),
        ('device_type', query['device_type']),
    ])


class StorageMongo(object):

    def insert_metadata_transform(
        self,
        documents,
        collection_object,
        tenant_code,
        project_id,
        keyword,
        locale,
        search_engine,
        device_type
    ):
        delete_query = {
            'tenant_code': tenant_code,
            'project_id': project_id,
            'keyword': keyword,
            'device_type': device_type,
            'search_engine': search_engine,
            'locale': locale
        }
        collection_object.remove(delete_query)
        bulk = collection_object.initialize_unordered_bulk_op()
        # Insert new documents with different tags
        for doc in documents:
            mDoc = dict(doc)
            # to be sure to avoid duplicate mongo object ids
            if '_id' in mDoc:
                mDoc.pop('_id')
            bulk.insert(mDoc)
        try:
            bulk.execute()
        except BulkWriteError as bwe:
            for item in bwe.details['writeErrors']:
                log_error(
                    tenant_code, project_id, keyword,
                    item['op']['url'], item['op']['_tag'], item['errmsg']
                )


class GenericStorage(object):

    def get_object(self, type_of_storage):
        generic_store_object = -1
        if type_of_storage == 'mongodb':
            generic_store_object = StorageMongo()
        return generic_store_object
