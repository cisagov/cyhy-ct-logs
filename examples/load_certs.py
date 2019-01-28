#!/usr/bin/env python3

import pprint
from datetime import datetime, timedelta
from collections import defaultdict

from cryptography import x509
from cryptography.hazmat.backends import default_backend
import dateutil.parser as parser

from pymodm.connection import connect
from pymodm import MongoModel, fields
from pymongo.write_concern import WriteConcern
from pymongo.operations import IndexModel
from pymongo import ASCENDING

from admiral.celery import celery
from admiral.certs.tasks import summary_by_domain, cert_by_id

PP = pprint.PrettyPrinter(indent=4)
PRETTY_NEW = timedelta(days=30)
ALMOST_EXPIRED = timedelta(days=30)
DOMAIN = 'us-cert.gov'


# https://tools.ietf.org/html/rfc5280#section-4.1.2.2


class Cert(MongoModel):
    log_id = fields.IntegerField(primary_key=True)
    serial = fields.CharField()  # 20 octets
    issuer = fields.CharField()
    not_before = fields.DateTimeField()
    not_after = fields.DateTimeField()
    pem = fields.CharField()
    subjects = fields.ListField(fields.CharField())

    class Meta:
        indexes = [IndexModel(keys=[
            ('issuer', ASCENDING),
            ('serial', ASCENDING)], unique=True),
            IndexModel(keys=[('subjects', ASCENDING)])]
        write_concern = WriteConcern(j=True)
        connection_alias = 'my-app'
        final = True


class PreCert(MongoModel):
    log_id = fields.IntegerField(primary_key=True)
    serial = fields.CharField()  # 20 octets
    issuer = fields.CharField()
    not_before = fields.DateTimeField()
    not_after = fields.DateTimeField()
    pem = fields.CharField()
    subjects = fields.ListField(fields.CharField())

    class Meta:
        indexes = [IndexModel(keys=[
            ('issuer', ASCENDING),
            ('serial', ASCENDING)], unique=True),
            IndexModel(keys=[('subjects', ASCENDING)])]
        write_concern = WriteConcern(j=True)
        connection_alias = 'my-app'
        collection_name = 'precert'
        final = True


def make_cert_from_pem(pem):
    x = x509.load_pem_x509_certificate(bytes(pem, 'utf-8'), default_backend())
    cn = x.subject.get_attributes_for_oid(
        x509.oid.NameOID.COMMON_NAME)[0].value
    try:
        san = x.extensions.get_extension_for_oid(
            x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value
        dns_names = set(san.get_values_for_type(x509.DNSName))
    except x509.extensions.ExtensionNotFound:  # craptacular interface you got there
        dns_names = set()
    try:
        x.extensions.get_extension_for_oid(
            x509.oid.ExtensionOID.PRECERT_POISON)
        precert_poison = True
    except x509.extensions.ExtensionNotFound:  # craptacular interface you got there
        precert_poison = False
    # TODO make sure the cn is a correct type
    # what the hell is going on here: https://crt.sh/?id=174654356
    # make sure the cn is in the dns_names
    dns_names.add(cn)

    # build a Cert Model object
    if precert_poison:
        cert = PreCert()
    else:
        cert = Cert()

    cert.serial = hex(x.serial_number)[2:]
    cert.precert = precert_poison
    cert.issuer = x.issuer.rfc4514_string()
    cert.not_before = x.not_valid_before
    cert.not_after = x.not_valid_after
    cert.pem = pem
    cert.subjects = dns_names
    return cert


def cert_id_exists(log_id):
    c = Cert.objects.raw({'_id': log_id})
    if c.count() > 0:
        return True
    c = PreCert.objects.raw({'_id': log_id})
    if c.count() > 0:
        return True
    return False


def get_new_log_ids(domain):
    print(f'requesting certificate list for: {DOMAIN}')
    cert_list = summary_by_domain.delay(DOMAIN, subdomains=True)
    cert_list = cert_list.get()
    for i in cert_list:
        log_id = i['min_cert_id']
        print(f'processing log_id: {log_id}... ', end='')
        # check to see if we have this certificate already
        if cert_id_exists(log_id):
            # we already have it, skip
            print('skipping')
        else:
            yield(log_id)
            print('done')


def main():
    connect("mongodb://logger:example@mongo:27017/certs", alias="my-app")
    for log_id in get_new_log_ids(DOMAIN):
        pem = cert_by_id.delay(log_id)
        pem = pem.get()
        cert = make_cert_from_pem(pem)
        cert.log_id = log_id
        cert.save()
    import IPython
    IPython.embed()  # <<< BREAKPOINT >>>


if __name__ == '__main__':
    main()
