import re
import tldextract


class TransformHelper(object):

    # Cleans URLs by removing http, https and www and returns the string
    @staticmethod
    def clean_url(url):
        remove_entities = ['http://', 'https://', 'www.']
        for entity in remove_entities:
            url = url.replace(entity, '')
        if url[-1] == '/':
            url = url[:-1]
        return url

    @staticmethod
    def extract_subdomain_domain_suffix(url):
        try:
            extracted_url = tldextract.extract(url)
            domain_name = extracted_url.domain
            suffix_name = extracted_url.suffix
            subdomain_name = extracted_url.subdomain
            clean_subdomain = re.sub(r'[^a-zA-Z0-9]', '', subdomain_name)
            if clean_subdomain == 'www':
                clean_subdomain = ''
            clean_domain = re.sub(r'[^a-zA-Z0-9]', '', domain_name)
            clean_suffix = re.sub(r'[^a-zA-Z0-9]', '', suffix_name)
            return (clean_subdomain, clean_domain, clean_suffix)
        except Exception as e:
            Exception(e)
            return None

    @staticmethod
    def domain_classify(mydomain, url):
        mydomain_suffix = TransformHelper.extract_subdomain_domain_suffix(mydomain)
        url_suffix = TransformHelper.extract_subdomain_domain_suffix(url)
        if (mydomain_suffix == url_suffix) and (TransformHelper.clean_url(mydomain) in TransformHelper.clean_url(url)):
            return 1
        return 0