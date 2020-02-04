from boto import sqs
from boto.sqs.message import Message


class QQueueConnection(object):
    __queue_connection = None

    def __init__(self, *args, **kwargs):
        self.region = kwargs.get('region', None)
        self.access_key = kwargs.get('access_key', None)
        self.secret_key = kwargs.get('secret_key', None)
        self.__queue_connection = sqs.connect_to_region(
            self.region, aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key)

    def create_queue(self, queue_name, **kwargs):
        visibility_timeout = kwargs.get("visibility_timeout", 30)
        return QQueue(queue=self.__queue_connection.create_queue(
            queue_name, visibility_timeout))

    def get_queue(self, queue_name, **kwargs):
        queue = self.__queue_connection.get_queue(queue_name)
        if queue is None:
            visibility_timeout = kwargs.get("visibility_timeout", 30)
            queue = self.__queue_connection.create_queue(
                queue_name, visibility_timeout)
        return QQueue(queue=queue)

    def delete_queue(self, queue):
        self.__queue_connection.delete_queue(queue.get_object())


class QQueue(object):
    __queue = None

    def __init__(self, *args, **kwargs):
        self.__queue = kwargs.get("queue", None)

    def get_object(self):
        return self.__queue

    def set_message(self, message):
        self.__queue.write(message.get_object())

    def get_message_count(self):
        return self.__queue.count()

    def get_messages(self, **kwargs):
        visibility_timeout = kwargs.get("visibility_timeout", 30)
        num_messages = kwargs.get("message_count", 1)
        message_list = []
        for message in self.__queue.get_messages(
                num_messages=num_messages, visibility_timeout=visibility_timeout):
            message_list.append(QMessage(message=message))
        return message_list

    def delete_message(self, message, **kwargs):
        return self.__queue.delete_message(message.get_object())


class QMessage(object):
    __message = None

    def __init__(self, *args, **kwargs):
        self.__message = kwargs.get("message", None)

    def get_object(self):
        return self.__message

    def set_body(self, message_body):
        if self.__message is None:
            self.__message = Message()
        self.__message.set_body(message_body)

    def get_body(self):
        return self.__message.get_body()
