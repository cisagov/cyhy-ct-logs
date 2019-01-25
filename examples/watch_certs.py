#!/usr/bin/env python3

import pprint
from datetime import datetime, timedelta

from cryptography import x509
from cryptography.hazmat.backends import default_backend
import dateutil.parser as parser

from admiral.celery import celery
from admiral.certs.tasks import *

PP = pprint.PrettyPrinter(indent=4)
PRETTY_NEW = timedelta(days=30)
ALMOST_EXPIRED = timedelta(days=30)
DOMAIN = 'dhs.gov'


# https://tools.ietf.org/html/rfc5280#section-4.1.2.2
# 1113870166

def main():

    utc_now = datetime.utcnow()
    print(f'requesting certificate list for: {DOMAIN}')
    cert_list = summary_by_domain.delay(DOMAIN, subdomains=True)
    print(f'found {len(cert_list.get())} matching certificates')
    for i in cert_list.get():
        not_before = parser.parse(i['not_before'])
        not_after = parser.parse(i['not_after'])
        age = utc_now - not_before
        life_remaining = not_after - utc_now
        print(f"{i['min_cert_id']}: {i['name_value']}")
        if age < PRETTY_NEW:
            print(f'\tNEW\tage is {age}')
        if life_remaining < ALMOST_EXPIRED:
            print(f'\tEXPIRING\texpires in {life_remaining}')
        else:
            print(f'\tOK\texpires in {life_remaining}')

    import IPython; IPython.embed() #<<< BREAKPOINT >>>

if __name__ == '__main__':
    main()
