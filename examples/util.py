"""Utility functions."""

import yaml
from pymodm.connection import connect


def load_config(filename='/run/secrets/mongo_yml'):
    """Load a configuration file."""
    print(f'Reading configuration from {filename}')
    with open(filename, 'r') as stream:
        config = yaml.load(stream)
    return config


def connect_from_config(config=None):
    """Create connections from a confguration."""
    if not config:
        config = load_config()
    connections = config['connections']
    for alias in connections.keys():
        connect(connections[alias]['uri'], alias=alias)


def trim_domains(domains):  # TODO make this more robust
    """Create a set of parent domain names from domain names.

    Arguments:
    domains -- a collection of domain strings

    Returns a set of trimmed domain names, converted to lowercase
    """
    trimmed = set()
    for domain in domains:
        domain = domain.lower()     # Ensure all domains are lowercase
        if domain.endswith('.fed.us'):
            trimmed.add('.'.join(domain.split('.')[-3:]))
        else:
            trimmed.add('.'.join(domain.split('.')[-2:]))
    return trimmed
