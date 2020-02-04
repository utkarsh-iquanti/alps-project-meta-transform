from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from django.conf import settings
from .queue import QQueueConnection
import time
import threading


class QQueueCommand(BaseCommand):
    # args = ''
    # help = ''

    # option_list = BaseCommand.option_list + (
    #     make_option('--threads',
    #                 default=1,
    #                 help='Number of threads to be spawned'),
    #     make_option('--message_retry_limit',
    #                 default=3,
    #                 help='The limit to the number of retries for a message'),
    #     make_option('--queue_retry_limit',
    #                 default=3,
    #                 help='The limit to the number of retries for a message'),
    #     make_option('--queue_retry_duration',
    #                 default=3,
    #                 help='The limit to the number of retries for a message'),
    #     make_option('--visibility_timeout',
    #                 default=3,
    #                 help='visibility_timeout for each message in queue'),
    #     make_option('--queue_name',
    #                 default=3,
    #                 help='Name for the queue'),
    # )

    def __init__(self, *args, **kwargs):
        self.threads = 0
        self.queue_retry_limit = 0
        self.queue_retry_duration = 0
        self.message_retry_limit = 0
        self.queue_name = ''
        self.retry_count = 0
        super(QQueueCommand, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        # parser.add_argument('total', type=int, help='Indicates the number of users to be created')
        parser.add_argument('-t', '--threads', type=int,
                            help='Number of threads to be spawned', default=1)
        parser.add_argument('-r', '--message_retry_limit', type=int,
                            help='The limit to the number of retries for a message', default=3)
        parser.add_argument('-qr', '--queue_retry_limit', type=int,
                            help='The limit to the number of retries for a message', default=3)
        parser.add_argument('-qrd', '--queue_retry_duration', type=int,
                            help='The limit to the number of retries for a message', default=3)
        parser.add_argument('-vi', '--visibility_timeout',
                            type=int, help='', default=3)
        parser.add_argument('-q', '--queue_name', type=str,
                            help='Name for the queue')
        

    def set_up(self, *args, **kwargs):
        self.threads = int(kwargs.get('threads', 1))
        self.queue_retry_limit = int(kwargs.get('queue_retry_limit', 3))
        self.queue_retry_duration = int(kwargs.get('queue_retry_duration', 30))

        # Changed retry limit to 100 temporarily
        self.message_retry_limit = int(kwargs.get('message_retry_limit', 100))
        self.queue_name = kwargs.get('queue_name', '')
        self.queue_visibility_timeout = int(
            kwargs.get('visibility_timeout', 30))
        queue_connection = QQueueConnection(region=settings.AWS_REGION,
                                            access_key=settings.AWS_ACCESS_KEY,
                                            secret_key=settings.AWS_SECRET_KEY)
        self.queue = queue_connection.get_queue(self.queue_name)

    def get_messages(self, message_count=1):
        while self.retry_count < self.queue_retry_limit:
            messages = self.queue.get_messages(
                message_count=message_count,
                visibility_timeout=self.queue_visibility_timeout)
            if len(messages) > 0:
                return messages
            else:
                self.retry_count += 1
                time.sleep(self.queue_retry_duration)
        raise CommandError('Number retries exceeded retry limit')

    def process_message(self, *args, **kwargs):
        raise NotImplementedError

    def handle(self, *args, **kwargs):
        self.set_up(*args, **kwargs)
        messages = self.get_messages()
        default_thread_count = len(threading.enumerate())
        while messages:
            if len(threading.enumerate()) - default_thread_count < self.threads:
                message_thread = threading.Thread(
                    target=self.process_message, args=(messages))
                message_thread.start()
                messages = self.get_messages()
            else:
                time.sleep(self.queue_retry_duration)
