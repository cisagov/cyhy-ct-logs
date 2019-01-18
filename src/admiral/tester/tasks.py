from celery import shared_task
from celery.utils.log import get_task_logger
import time
import random


logger = get_task_logger(__name__)

@shared_task
def add(x, y):
    logger.info('Adding {0} + {1}'.format(x, y))
    return x + y

@shared_task
def slow_add(x, y):
    r = add(x, y)
    logger.info('Sleeping')
    time.sleep(5)
    return r

@shared_task
def bad_add(x,y):
    r = slow_add(x, y)
    if random.choice([True, False]):
        logger.info('Failing on purpose')
        raise Exception('Adding is hard')
    else:
        return r

@shared_task(   autoretry_for=(Exception,),
                retry_backoff=True,
                retry_jitter=True,
                retry_kwargs={'max_retries': 3})
def better_add(x,y):
    return bad_add(x,y)

@shared_task
def mul(x, y):
    logger.info('Multipling {0} + {1}'.format(x, y))
    return x * y


@shared_task
def xsum(numbers):
    logger.info('Summing {0}'.format(numbers))
    return sum(numbers)
