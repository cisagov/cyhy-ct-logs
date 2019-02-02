import yaml
from pymodm.connection import connect
from pymodm import context_managers

def load_config(filename='/run/secrets/mongo_yml'):
    print(f'Reading configuration from {filename}')
    with open(filename, 'r') as stream:
        config = yaml.load(stream)
    return config

def connect_from_config(config=None):
    if not config:
        config = load_config()
    connections = config['connections']
    for alias in connections.keys():
        connect(connections[alias]['uri'], alias=alias)
