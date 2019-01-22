#!/usr/bin/env pytest -vs

import pprint

import pytest
from cryptography import x509
from cryptography.hazmat.backends import default_backend

from admiral.port_scan.tasks import *

PP = pprint.PrettyPrinter(indent=4)

@pytest.fixture(scope="module")
def celery():
    from admiral.celery import celery
    return celery

@pytest.fixture(scope="module")
def host_ip():
    '''resolve and return host_ip as a string'''
    import dns.resolver
    query = dns.resolver.query('scanme.nmap.org')
    assert len(query) > 0, 'could not resolve target host name'
    return query[0].address

class TestPortScans:
    def test_up_scan(self, celery, host_ip):
        ns1 = up_scan.delay(host_ip)
        PP.pprint(ns1.get())

    def test_port_scan(self, celery, host_ip):
        ns2 = port_scan.delay(host_ip)
        PP.pprint(ns2.get())
