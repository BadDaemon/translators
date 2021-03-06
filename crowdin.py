#!/usr/bin/env python
from __future__ import print_function
import argparse
import codecs
import json
import languages
import re
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
    parser.add_argument('-d', '--delete-inactive', action='store_true',
                        help='Whether to delete inactive members from the project')
    parser.add_argument('-o', '--older-than', default=6,
                        help='Filter inactive users who are older than the given amount of months (default: 6)')
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
    inactive = []
    removed = []

    crowdin_to_name = languages.getLanguages()
    members = Members(cookies, useragent, args)
    for member in members:
        for person in member:
            p = Member(cookies, useragent, person['id'])
            info = p.get()
            name = info['name']
            print(name, end=': ')
            if person['role'] == 'Owner':
                print()
                continue
            if person['role'] == 'Manager':
                managers.append(info['name'])
                print()
                continue
            if person['role'] == 'Proofreader':
                global_proofreaders.append(name)

            if not 'groups' in info: continue
            for k in info['groups']:
                v = info['groups'][k]
                if v != 'leader' and person['role'] != 'Proofreader': continue
                if int(k) in crowdin_to_name:
                    lang = crowdin_to_name[int(k)]
                else:
                    lang = 'Unknown'
                print(lang, end=' ')
                leads.setdefault(lang, []).append(name)

            commentedStrings = info['commented']['strings']
            commentedWords = info['commented']['words']
            approvedStrings = info['approved']['strings']
            translatedStrings = info['translated']['strings']
            months = 0
            dateAgo = re.search("(\d+) months ago", info['last_seen']['date_ago'])
            if dateAgo != None:
                months = int(dateAgo.group(1))
            if (dateAgo != None and months >= args.older_than
                    and commentedStrings == 0
                    and (commentedWords == 0 or commentedWords == '-')
                    and approvedStrings == 0 and translatedStrings == 0
                    and name not in managers
                    and name not in global_proofreaders
                    and name not in leads):
                if args.delete_inactive:
                    print("Removing user due to inactivity")
                    removed.append(name)
                    p.remove()
                else:
                    inactive.append(name)
            print()

    proofreaders = OrderedDict()
    proofreaders["managers"] = managers
    proofreaders["global_proofreaders"] = global_proofreaders
    proofreaders["languages"] = leads

    with codecs.open("proofreaders.json", "w", "utf-8-sig") as temp:
        temp.write(json.dumps(proofreaders, ensure_ascii=False, sort_keys=False, indent=4, separators=(',', ': ')))

    with codecs.open("inactive.json", "w", "utf-8-sig") as temp:
        temp.write(json.dumps(inactive, ensure_ascii=False, sort_keys=False, indent=4, separators=(',', ': ')))

    with codecs.open("removed.json", "w", "utf-8-sig") as temp:
        temp.write(json.dumps(removed, ensure_ascii=False, sort_keys=False, indent=4, separators=(',', ': ')))

def main():
    signal.signal(signal.SIGINT, signal_handler)

    check_config()
    args = parse_args()

    if args.include_managers:
        print("Generating list including managers")
    else:
        print("Generating list without managers")

    if args.delete_inactive:
        print("Deleting inactive contributors (member >= {} months, no activity ever)".format(args.older_than))

    get_members(args)

if __name__ == '__main__':
    main()

