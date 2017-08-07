# from python library
import logging

# from third-party application
from django.utils.timezone import localtime, now

logger = logging.getLogger(__name__)


def log_start_time():
    logger.debug('Start Time of Function - %s' % localtime(now()))


def log_end_time():
    logger.debug('End Time of Function - %s' % localtime(now()))


def log_enter_atomic_trans():
    logger.debug('Entering Atomic Transaction')


def log_exit_atomic_trans():
    logger.debug('Exiting Atomic Transaction')