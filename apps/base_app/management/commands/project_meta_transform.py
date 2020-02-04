import json
import time
import datetime
from datetime import datetime as dt
import requests
import logging

from rest_framework import status

from collections import OrderedDict
from django.utils import timezone
from django.core.cache import cache
from apps.base_app.services.exceptions import QException, AlpsException
from apps.base_app.services.command import QQueueCommand
from django.conf import settings

from iqstorage.dc.keyword import KeywordSERPDataForSEOData
import iqstorage.common.storage_exceptions as s3e
from iqdcutils.serp.dataforseo.rank_utils import RankUtils


from apps.base_app.services.db_factory import GenericStorage
from apps.base_app.services.helper import TransformHelper as Helper
import collections


DEFAULT_RANK = 121
DATA_NOT_AVAILABLE = None
DATA_NA = 'NA'
SEARCH_COMPETITOR_DOMAIN = '-1'
activity_logger = logging.getLogger('activity.transform.keyword')
error_logger = logging.getLogger('error.transform.keyword')

DEFAULT_S3_OBJECT_NAME = 'latest'

def log_error(msg, error=None):
    if error is not None:
        error_logger.error('Project Metadata Transform|MSG:%s|ERROR:%s' % (msg, str(error)))
    else:
        error_logger.error('Project Metadata Transform|MSG:%s|ERROR:%s' % msg)


class ProjectMetadataTransform(object):

    # The initial constructor for the overall project transform. Contains Collection objects for all
    def __init__(self):
        self.storage_object = GenericStorage().get_object('mongodb')
        self.variables_to_ignore = [
            "_id",
            "_tag",
            "created_date",
            "updated_date",
            "current_date",
            "page",
            "tenant_code",
            "brand_pack_link_count",
            "result_type",
            "base_domain"
        ]
        # Keyword level common default values
        self.default_common_values = {
            'rank': DEFAULT_RANK,
            'blended_rank': DEFAULT_RANK,
            'organic_rank': DEFAULT_RANK,
        }

    # Checks if the URL belongs to our domains or any of our competitors
    # Tells us if the url is relevant for our project. Returns 1/0
    def is_url_relevant(self, url):
        if url is not None:
            for alias_id in self.relevant_domain_list:
                for domain in self.relevant_domain_list[alias_id]['urls']:
                    if Helper.domain_classify(domain, url):
                        return 1
        return 0

    def get_alias_id(self, url):
        if url is not None:
            for alias_id in self.relevant_domain_list:
                for domain in self.relevant_domain_list[alias_id]['urls']:
                    if Helper.domain_classify(domain, url):
                        return str(alias_id)
        return SEARCH_COMPETITOR_DOMAIN

    def get_non_ranking_target_urls(self, target_urls, sorted_serp):
        ranking_urls = [rank['url'] for rank in sorted_serp]
        non_ranking_target_urls = list(set(target_urls).difference(ranking_urls))
        sample_kwd_doc = sorted_serp[-1].copy()
        for value in self.variables_to_ignore:
            if value in sample_kwd_doc:
                sample_kwd_doc.pop(value)

        for target_url_data in non_ranking_target_urls:
            target_url_doc = sample_kwd_doc.copy()
            target_url_doc['url'] = target_url_data
            target_url_doc.update(self.default_common_values)
            sorted_serp.append(target_url_doc)

    def is_project_relevant_url(self, each_rank, last_organic_rank):
        if (last_organic_rank <= 10) or \
                (self.is_url_relevant(each_rank['url'])) or \
                (each_rank.get('page', None) == 1):
            return True
        return False

    def get_my_domains(self):
        my_domains = self.project_details['domains'] + self.project_details['subdomains']
        target_urls = [theme['target_url']
                       for theme in self.project_details['data']['themes']
                       if self.keyword in theme['keywords'] and \
                       theme['target_url'] and \
                       theme['target_url'].lower() != 'not set'
        ]
        my_domains += target_urls
        return my_domains, target_urls

    def get_relevant_domain_list(self, my_domains):
        relevant_domain_list = dict()
        relevant_domain_list["0"] = {
            'alias_name': '__me__',
            'urls': list(set(my_domains))
        }
        relevant_domain_list.update(self.project_details['business_competitor'])
        return collections.OrderedDict(sorted(relevant_domain_list.items()))

    def insert_for_date(self, keyword, req_date, locale, search_engine, device_type, transform_date, serp_data):
        try:
            # Get Docs from KWD-URL Transform
            sorted_serp = sorted(serp_data, key = lambda k: k['blended_rank'])

            # This is for aggregating some additional project_keyword_url_metrics
            project_keyword_url_list = []
            base_project_doc = {}
            self.keyword = keyword

            # Get all relevent my domain, competitor domains and URLs
            my_domains, target_urls = self.get_my_domains()
            self.relevant_domain_list = self.get_relevant_domain_list(my_domains)
            sample_kwd_doc = sorted_serp[-1].copy()

            # Append non-ranking target urls coming from themes
            self.get_non_ranking_target_urls(target_urls, sorted_serp)

            current_date = req_date
            tenant_code = self.project_message['tenant_code']
            project_id = self.project_message['project_id']

            # Adding project specific details common accross all URLs of the keyword
            base_project_doc['tenant_code'] = tenant_code
            base_project_doc['project_id'] = project_id
            base_project_doc['keyword'] = keyword
            base_project_doc['keyword_id'] = self.project_details['data']['keywords'][keyword]['id']
            base_project_doc['keyword_type'] = self.project_details['data']['keywords'][keyword]['type']
            base_project_doc['created_date'] = datetime.datetime.now()
            base_project_doc['search_engine'] = search_engine
            base_project_doc['locale'] = locale
            base_project_doc['device_type'] = device_type

            # TILL Top 10 organic ranks or my domain/competitors domains or Page 1 results
            last_organic_rank = None
            for each_rank in sorted_serp:
                organic_rank = each_rank['organic_rank']
                last_organic_rank = organic_rank if organic_rank is not None else last_organic_rank
                if self.is_project_relevant_url(each_rank, last_organic_rank):
                    # To not go beyond organic rank 10 for search competitors or all page 1 results
                    last_organic_rank = 11 if organic_rank == 10 else last_organic_rank

                    project_document = base_project_doc.copy()

                    # Retain fields from KWD doc
                    for each_raw_field in each_rank:
                        if each_raw_field not in self.variables_to_ignore:
                            project_document[each_raw_field] = each_rank[each_raw_field]


                    # Adding domain specific details
                    alias_id = self.get_alias_id(each_rank['url'])
                    project_document['alias_id'] = alias_id
                    if alias_id == SEARCH_COMPETITOR_DOMAIN:
                        project_document['alias_name'] = DATA_NA
                    else:
                        project_document['alias_name'] = self.relevant_domain_list[alias_id]['alias_name']
                    project_keyword_url_list.append(project_document)


            # Create Dummy entries for non organic ranking my domain and competitor domains
            ranking_domains = [
                each['alias_id'] for each in project_keyword_url_list \
                   if each['organic_rank'] is not DATA_NOT_AVAILABLE
            ]

            non_ranking_domains = list(
                set(self.relevant_domain_list.keys()).difference(ranking_domains)
            )

            sample_project_doc = dict(
                (k, DATA_NOT_AVAILABLE) for k, v in \
                    sample_kwd_doc.copy().items()
            )
            for value in self.variables_to_ignore:
                if value in sample_kwd_doc:
                    sample_project_doc.pop(value)

            sample_project_doc.update(base_project_doc)

            for alias_id in non_ranking_domains:
                alias_name = self.relevant_domain_list[alias_id]['alias_name']
                project_document = sample_project_doc.copy()
                project_document.update(self.default_common_values)

                # Domain specific dummy details
                project_document.update({
                    'alias_id': alias_id,
                    'alias_name': alias_name,
                })
                project_keyword_url_list.append(project_document)
            self.storage_object.insert_metadata_transform(
                project_keyword_url_list,
                settings.PROJECT_KW_URL_METADATA_COLLECTION,
                tenant_code,
                project_id,
                keyword,
                locale,
                search_engine,
                device_type
            )
        except Exception as e:
            log_msg = 'Error in inserting data for date for keyword: %s' % keyword
            log_error(log_msg, e)
            raise AlpsException(e)

    def transform(self, project_details, project_message):
        try:
            todays_date = timezone.datetime.now()
            self.project_message = project_message
            keyword_dict, serp_data = self.get_keyword_metrics(project_message)

            keyword = project_message['keyword']
            device_type = project_message['device_type']

            self.project_details = project_details
            if 'transform_date' not in project_message:
                project_message['transform_date'] = str(timezone.datetime.now())

            date_object = timezone.datetime.strptime(
                str(project_message['transform_date']),
                "%Y-%m-%d %H:%M:%S.%f"
            )
            current_date = timezone.datetime.strftime(
                date_object,
                "%Y%m%d"
            )
            if keyword in project_details['data']['keywords']:
                for locale in project_details['locales']:
                    for search_engine in project_details['search_engines']:
                        if serp_data:
                            self.insert_for_date(
                                keyword=keyword,
                                req_date=current_date,
                                locale=locale,
                                search_engine=search_engine,
                                device_type=device_type,
                                transform_date=project_message['transform_date'],
                                serp_data=serp_data
                            )
                        else:
                            log_msg = 'Keyword:|%s| serp_tag:|%s| not in KWD Transform' \
                                      % (keyword, serp_tag)
                            log_error(log_msg)
                            raise AlpsException('Keyword:|%s| serp_tag:|%s| not in KWD Transform' % \
                                                (keyword, serp_tag))
            else:
                log_msg = 'Keyword:|%s| not in Project:|%s|' \
                          % (keyword, project_details['id'])
                log_error(log_msg)
                raise AlpsException('Keyword:|%s| not in Project:|%s|' % (keyword, project_details['id']))
        except Exception as e:
            log_msg = 'Error in running project transform'
            log_error(log_msg)
            raise e

    def get_s3_object_name(self, date):
        """
        :param date_str: should be datetime_object or str(datetime_object)
        :return: corresponding date
        """
        try:
            date_str = str(date)
            date_object = dt.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
            s3_object_name = date_object.strftime('%Y%m%d')
            return s3_object_name
        except Exception as e:
            log_msg = 'Error in getting s3 objects. Message: %s' % \
                      (str(e.message))
            log_error(log_msg)
            AlpsException(e)

    def get_keyword_metrics(self, project_message):
        keyword_dict = {}

        serp_data_dict = self.get_serp_data(project_message)

        if not serp_data_dict or len(serp_data_dict.get('serp_list', [])) == 0:
            # to handle old scenarios where dummy entries in DC are created
            serp_data_dict = None

        if serp_data_dict is not None:
            keyword_dict['serp_date'] = serp_data_dict['rank_date']
            url_serp_list = serp_data_dict['serp_list']
        else:
            # Rank data not available. LOG.
            log_msg = 'No Rank data for keyword: %s' % project_message['keyword']
            log_error(log_msg)
            keyword_dict['serp_date'] = DATA_NOT_AVAILABLE
            url_serp_list = list()
        return keyword_dict, url_serp_list

    def get_serp_data(self, project_message):
        serp_data_dict = {}
        serp_kwargs = dict(
            keyword=project_message['keyword'],
            locale=project_message['locale'],
            device_type=project_message['device_type'],
            search_engine=project_message['search_engine']
        )
        try:
            serp_response = KeywordSERPDataForSEOData(**serp_kwargs).get()
            r = RankUtils()
            serp_data_dict = r.get_all_results(serp_response, False)
        except s3e.FileNotFound as e:
            # some other serious issue. Log and raise
            pass
        return serp_data_dict


class Command(QQueueCommand):
    def get_project_details(self, tenant, project_id):
        try:
            project_cache_key = settings.ALPS_PROJECT_CACHE_KEY % (tenant, str(project_id))
            # project_details = cache.get(project_cache_key, None)
            project_details = None
            if project_details is None or 'data' not in project_details:
                url_scheme = 'https' if settings.SESSION_COOKIE_SECURE is True else 'http'
                url_str = url_scheme + '://%(ip)s/alps/manage/%(' \
                                       'tenant)s/projects/%(' \
                                       'pid)s/details?session_token=%(token)s'
                api_call_url = url_str % dict(
                ip=settings.API_IP_ADDRESS, tenant=tenant, pid=project_id,
                    token=settings.ALPS_APPLICATION_SESSION_TOKEN
                )
                response = requests.get(url=api_call_url)
                if response.status_code == status.HTTP_200_OK:
                    project_details = response.json()
                else:
                    raise Exception('Server Error')
            project_details['business_competitor'] = json.loads(json.dumps(project_details.get('business_competitor')))
            return project_details
        except Exception as e:
            log_msg = 'Project details not fetched for tenant_code: %s project: %s' % (tenant, project_id)
            log_error(log_msg, e)
            raise e

    def process_message(self, *args, **kwargs):
        project_message = json.loads(args[0].get_body())
        tenant = project_message['tenant_code']
        locale = project_message['locale']
        keyword = project_message['keyword']
        device_type = project_message['device_type']
        project_id = int(project_message['project_id'])
        try:
            project_details = self.get_project_details(
                tenant=tenant, project_id=project_id
            )
            transform_object = ProjectMetadataTransform()
            transform_object.transform(project_details, project_message)
        except Exception as e:
            log_msg = 'Transform failed for tenant_code: %s project: %s keyword: %s' % (tenant, project_id, keyword)
            log_error(log_msg, e)
            # retry if needed
        finally:
            self.queue.delete_message(args[0])
