#!/usr/bin/env python

import argparse
import yaml
import os
import requests
import pydoc

FIREPIT_SESSION_URL_PREFIX = 'https://firepit.example.net/#/session/'
args = ''
log_url = ''

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('log_url',
                        help='URL of the Bamboo log',
                        type=str)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-r', '--raw',
                       help='View the log without any filters',
                       action='store_true')
    group.add_argument('-e', '--errors',
                       help='Filter for errors',
                       action='store_true')
    args = parser.parse_args()
    return args

def get_creds():
    home = os.path.expanduser('~')
    credentials_file = home + '/.credentials'
    if os.path.isfile(credentials_file):
        credentials = yaml.load(open(credentials_file))
        username = credentials['sqsp-ldap']['username']
        password = credentials['sqsp-ldap']['password']
        return username, password
    else:
        print(credentials_file + ' does not exist.')
        sys.exit(1)

def filter_errors(log):
    firepit_fail = 'Firepit caused this deploy to fail'
    for line in log.splitlines():
        if 'Created Firepit Session' in line:
            session_id = line.split('"')[1]
        if firepit_fail in line:
            firepit_url = FIREPIT_SESSION_URL_PREFIX + session_id
            print('Error: ' + firepit_fail)
            print('URL: ' + firepit_url)
            user_choice = raw_input('Do you want to open the Firepit session in a browser? (y/N) ').lower() or 'n'
            if user_choice == 'y':
                os.system('open ' + firepit_url)

def main():
    args = get_args()
    username, password = get_creds()
    url = args.log_url
    r = requests.get(url, auth=(username, password))

    if args.raw:
        pydoc.pipepager(r.text, cmd='less')
    elif args.errors:
        filter_errors(r.text)


if __name__ == '__main__':
    main()
