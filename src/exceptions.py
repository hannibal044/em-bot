import logging

logger = logging.getLogger(__name__)


class BotException(Exception):
    def __init__(self, error=None, message=None):
        self.error = error
        self.message = message
        super().__init__(self.message)
        logger.error(self.error)
