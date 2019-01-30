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
DOMAIN = 'cyber.dhs.gov'


# https://tools.ietf.org/html/rfc5280#section-4.1.2.2

class Cert(MongoModel):
    log_id = fields.IntegerField(primary_key=True)
    serial = fields.CharField()  # 20 octets
    issuer = fields.CharField()
    not_before = fields.DateTimeField()
    not_after = fields.DateTimeField()
    sct_or_not_before = fields.DateTimeField()
    sct_exists = fields.BooleanField()
    pem = fields.CharField()
    subjects = fields.ListField(fields.CharField())

    def x509(self):
        return x509.load_pem_x509_certificate(bytes(self.pem, 'utf-8'), default_backend())

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
    sct_or_not_before = fields.DateTimeField()
    sct_exists = fields.BooleanField()
    pem = fields.CharField()
    subjects = fields.ListField(fields.CharField())

    def x509(self):
        return x509.load_pem_x509_certificate(bytes(self.pem, 'utf-8'), default_backend())

    class Meta:
        indexes = [IndexModel(keys=[
            ('issuer', ASCENDING),
            ('serial', ASCENDING)], unique=True),
            IndexModel(keys=[('subjects', ASCENDING)])]
        write_concern = WriteConcern(j=True)
        connection_alias = 'my-app'
        collection_name = 'precert'
        final = True


class Domain(MongoModel):
    domain = fields.CharField(primary_key=True)


def get_earliest_sct(xcert):
    '''Calculate the earliest time this certificate was logged to a CT log.
    If it was not logged by the CA, then the not_before time is returned.

    Returns (datetime, bool):
        datetime: the earliest calculated date.
        bool: True if an SCT was used, False otherwise
    '''
    try:
        earliest = datetime.max
        scts = xcert.extensions.get_extension_for_class(
            x509.PrecertificateSignedCertificateTimestamps).value
        for sct in scts:
            earliest = min(earliest, sct.timestamp)
        return earliest, True
    except x509.extensions.ExtensionNotFound:
        return xcert.not_valid_before, False


def is_poisioned(xcert):
    try:
        xcert.extensions.get_extension_for_oid(
            x509.oid.ExtensionOID.PRECERT_POISON)
        return True
    except x509.extensions.ExtensionNotFound:
        return False


def get_sans_set(xcert):
    try:
        san = xcert.extensions.get_extension_for_oid(
            x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value
        dns_names = set(san.get_values_for_type(x509.DNSName))
    except x509.extensions.ExtensionNotFound:
        dns_names = set()
    cn = xcert.subject.get_attributes_for_oid(
        x509.oid.NameOID.COMMON_NAME)[0].value

    # TODO make sure the cn is a correct type
    # what the hell is going on here: https://crt.sh/?id=174654356
    # ensure the cn is in the dns_names
    dns_names.add(cn)
    return dns_names


def make_cert_from_pem(pem):
    xcert = x509.load_pem_x509_certificate(
        bytes(pem, 'utf-8'), default_backend())
    dns_names = get_sans_set(xcert)

    # use separate collections for precerts and certs
    if is_poisioned(xcert):
        cert = PreCert()
    else:
        cert = Cert()

    sct_or_not_before, sct_exists = get_earliest_sct(xcert)

    cert.serial = hex(xcert.serial_number)[2:]
    cert.issuer = xcert.issuer.rfc4514_string()
    cert.not_before = xcert.not_valid_before
    cert.not_after = xcert.not_valid_after
    cert.sct_or_not_before = sct_or_not_before
    cert.sct_exists = sct_exists
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
    cert = Cert.objects.get({'_id': 1017984548}).x509()
    scts = cert.extensions.get_extension_for_class(
        x509.PrecertificateSignedCertificateTimestamps).value
    import IPython;IPython.embed()  # <<< BREAKPOINT >>>


if __name__ == '__main__':
    main()
