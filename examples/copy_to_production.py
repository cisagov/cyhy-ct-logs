#!/usr/bin/env python3

from models import Cert, Agency, Domain
from util import connect_from_config

from pymodm import context_managers
from tqdm import tqdm


def main():
    connect_from_config()
    # Copy all documents from certs collection
    all_certs = Cert.objects.all()
    for cert in tqdm(all_certs, total=all_certs.count(), desc='Copy', unit='certs'):
        with context_managers.switch_connection(Cert, 'production'):
            cert.save()
    # Copy all documents from precerts collection
    with context_managers.switch_collection(Cert, 'precerts'):
        all_certs = Cert.objects.all()
        for cert in tqdm(all_certs, total=all_certs.count(), desc='Copy', unit='precerts'):
            with context_managers.switch_connection(Cert, 'production'):
                cert.save()


if __name__ == '__main__':
    main()
