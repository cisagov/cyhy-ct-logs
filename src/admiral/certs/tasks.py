import sys
import ipaddress
import traceback
import requests
import json
import re

from celery import shared_task, states
from celery.utils.log import get_task_logger
from celery.exceptions import Ignore

logger = get_task_logger(__name__)

# regexr.com/3e8n2
DOMAIN_NAME_RE = re.compile(
    r'^((?:([a-z0-9]\.|[a-z0-9][a-z0-9\-]{0,61}[a-z0-9])\.)+)'
    r'([a-z0-9]{2,63}|(?:[a-z0-9][a-z0-9\-]{0,61}[a-z0-9]))\.?$'
)

@shared_task(   autoretry_for=(Exception,requests.HTTPError),
                retry_backoff=True,
                retry_jitter=True,
                retry_kwargs={'max_retries': 3})
def summary_by_domain(domain, subdomains=True, expired=False):
    # validate input
    m = DOMAIN_NAME_RE.match(domain)
    logger.info(f'Fetching certs from CT log for domain: {domain}.')
    if m == None:
        raise ValueError('invalid domain name format')

    wildcard = '%.' if subdomains else ''
    expired = '' if expired else '&exclude=expired'

    url = f'https://crt.sh/?Identity={wildcard}{domain}{expired}&output=json'
    # TODO: make two queries
    req = requests.get(url, headers={'User-Agent': 'cyhy/2.0.0'})

    if req.ok:
        data = json.loads(req.content)
        return data
    else:
        req.raise_for_status()

@shared_task(   autoretry_for=(Exception,requests.HTTPError),
                retry_backoff=True,
                retry_jitter=True,
                retry_kwargs={'max_retries': 3})
def cert_by_id(id):
    logger.info(f'Fetching cert data from CT log for id: {id}.')

    url = f'https://crt.sh/?d={id}'
    req = requests.get(url, headers={'User-Agent': 'cyhy/2.0.0'})

    if req.ok:
        return req.content.decode()
    else:
        req.raise_for_status()