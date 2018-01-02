#!/usr/bin/env python
from __future__ import print_function
import argparse
import codecs
import json
import languages
import signal
import sys

from classes import Members, Member
from collections import OrderedDict
from config import config

useragent = ''
cookies = {}

def parse_args():
    parser = argparse.ArgumentParser(
        description="Synchronising LineageOS' translators with Crowdin")
    parser.add_argument('-m', '--include-managers', action='store_true',
                        help='Include managers, only possible if you are a manager yourself!')
    parser.add_argument('-N', '--per-page', default=30,
                        help='How many translators should be requested per page (default: 30)')
    return parser.parse_args()

def check_config():
    global useragent
    global cookies
    if not 'useragent' in config or config['useragent'].strip() == "" \
        or not 'cookies' in config or config['cookies'].strip() == "":
            print("Fill in the config.py file!")
            exit()

    useragent = config['useragent']
    cookies = {v.split('=')[0]: v.split('=')[1] for v in config['cookies'].split()}
    if not 'csrf_token' in cookies:
        print("Missing 'csrf_token' in cookie-string")

def signal_handler(signal, frame):
    print()
    print("Ctrl+C detected, aborting!")
    sys.exit(0)

def get_members(args):
    managers = []
    global_proofreaders = []
    leads = {}

    crowdin_to_name = languages.getLanguages()
    members = Members(cookies, useragent, args)
    for member in members:
        for person in member:
            p = Member(cookies, useragent, person['id'])
            info = p.get()
            print(info['name'], end=': ')
            if person['role'] == 'Owner':
                print()
                continue
            if person['role'] == 'Manager':
                managers.append(info['name'])
                print()
                continue
            if person['role'] == 'Proofreader':
                global_proofreaders.append(info['name'])
            if not 'groups' in info: continue
            for k in info['groups']:
                v = info['groups'][k]
                if v != 'leader' and person['role'] != 'Proofreader': continue
                if int(k) in crowdin_to_name:
                    lang = crowdin_to_name[int(k)]
                else:
                    lang = 'Unknown'
                print(lang, end=' ')
                leads.setdefault(lang, []).append(info['name'])
            print()

    proofreaders = OrderedDict()
    proofreaders["managers"] = managers
    proofreaders["global_proofreaders"] = global_proofreaders
    proofreaders["languages"] = leads

    with codecs.open("proofreaders.json", "w", "utf-8-sig") as temp:
        temp.write(json.dumps(proofreaders, ensure_ascii=False, sort_keys=False, indent=4, separators=(',', ': ')))

def main():
    signal.signal(signal.SIGINT, signal_handler)

    check_config()
    args = parse_args()

    if args.include_managers:
        print("Generating list including managers")
    else:
        print("Generating list without managers")

    get_members(args)

if __name__ == '__main__':
    main()

