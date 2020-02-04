import logging


class QException(Exception):
    def __init__(self, *args, **kwargs):
        super(QException, self).__init__(*args, **kwargs)


class AlpsException(Exception):
    def __init__(self, *args, **kwargs):
        super(AlpsException, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger('Logging')
        self.logger.exception(args)
