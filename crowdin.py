#!/usr/bin/env python
from __future__ import print_function
import codecs
import json
import languages
import requests
import sys

from collections import OrderedDict
from config import config

if not 'useragent' in config or config['useragent'].strip() == "" \
    or not 'cookies' in config or config['cookies'].strip() == "":
        print("Fill in the config.py file!")
        exit()

useragent = config['useragent']
cookies = {v.split('=')[0]: v.split('=')[1] for v in config['cookies'].split()}
if not 'csrf_token' in cookies:
    print("Missing 'csrf_token' in cookie-string")

memberListUri = 'https://crowdin.com/group_actions/members_list'
asManager = False
if len(sys.argv) > 1:
    arg1 = sys.argv[1]
    if arg1 == '--manager':
        memberListUri = 'https://crowdin.com/project_actions/members_list'
        asManager = True

if asManager:
    print("Generating list including managers")
else:
    print("Generating list without managers")

class Members:
    def __init__(self, cookies, ua):
        self.uri = memberListUri
        self.cookies = cookies
        self.ua = ua
        self.total = 3000

    def __iter__(self):
        self.cur_page = 0
        return self

    def __next__(self):
        if self.cur_page * 30 > self.total:
            raise StopIteration
        print("Getting members on page {}".format(self.cur_page+1))
        data = {
                'project_id': '237414', # LineageOS
                'filter_role': '',
                'filter_language': '',
                'target_language_id': '4',
                'page': str(self.cur_page+1),
                'sortname': 'role',
                'sortorder': 'asc',
                'rp': '30',
                'filter': '',
                'request': 1
            }
        headers = {
                'referer': 'http://translate.lineageos.org/project/lineageos/translators',
                'x-csrf-token': cookies['csrf_token'],
                'user-agent': self.ua,
                'x-requested-with': 'XMLHttpRequest',
                }
        r = requests.post(self.uri, cookies=self.cookies, data=data, headers=headers)
        self.cur_page += 1
        #print(json.dumps(r.json(), indent=4, separators=(',', ': ')))
        self.total = int(r.json()['total'])
        return r.json()['rows']

    def next(self):
        return self.__next__()

class Member:
    def __init__(self, cookies, ua, uid):
        self.params = {'user_id': uid, 'project_id': 237414}
        self.cookies = cookies
        self.ua = ua
        self.uri = 'http://translate.lineageos.org/project_actions/translator_info'

    def get(self):
        headers = {
                'referer': 'http://translate.lineageos.org/project/lineageos/translators',
                'x-csrf-token': cookies['csrf_token'],
                'user-agent': self.ua,
                'x-requested-with': 'XMLHttpRequest',
        }
        r = requests.get(self.uri, cookies=self.cookies, params=self.params, headers=headers)
        #print(json.dumps(r.json()))
        return r.json()['data']

m = Members(cookies, useragent)

managers = []
global_proofreaders = []
leads = {}

crowdin_to_name = languages.getLanguages()

for a in m:
    for person in a:
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
            #if lang not in leads:
            #    leads[lang] = []
            #leads[lang].append(info['name'])
            leads.setdefault(lang, []).append(info['name'])
            
        print()

proofreaders = OrderedDict()
proofreaders["managers"] = managers
proofreaders["global_proofreaders"] = global_proofreaders
proofreaders["languages"] = leads

with codecs.open("proofreaders.json", "w", "utf-8-sig") as temp:
    temp.write(json.dumps(proofreaders, ensure_ascii=False, sort_keys=False, indent=4, separators=(',', ': ')))

