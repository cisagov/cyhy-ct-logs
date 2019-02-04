#!/usr/bin/env python3
'''Mongo document copier.
Be careful, this can easily give you a bad day.

Usage:
  doc-copy <from_connection> <to_connection>
  doc-copy --list-connections
  doc-copy (-h | --help)
  doc-copy --version

 Options:
    -l --list-connections   List the available connections.
'''
import sys

from models import Cert, Agency, Domain
from util import load_config, connect_from_config

from pymodm import context_managers
from tqdm import tqdm


def copy_all(model, from_alias, to_alias):
    print(f'Querying all {model} from {from_alias}')
    with context_managers.switch_connection(model, from_alias):
        all = model.objects.all()
        print(f'Saving all {model} into {to_alias}')
        for x in tqdm(all, total=all.count(), desc='Copy', unit='docs'):
            with context_managers.switch_connection(model, to_alias):
                x.save()


def print_connections():
    config = load_config()
    print('Connections in configuration: ')
    for i in list(config['connections'].keys()):
        print(f'\t{i}')


def main():
    from docopt import docopt
    args = docopt(__doc__, version='v0.0.1')

    if args['--list-connections']:
        print_connections()
        sys.exit(0)

    from_alias = args['<from_connection>']
    to_alias = args['<to_connection>']

    # connect to databases
    connect_from_config()

    # Copy all documents from certs collection
    copy_all(Cert, from_alias, to_alias)

    # Copy all documents from precerts collection
    with context_managers.switch_collection(Cert, 'precerts'):
        copy_all(Cert, from_alias, to_alias)


if __name__ == '__main__':
    main()
