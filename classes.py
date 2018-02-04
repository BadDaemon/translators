import requests

class Members:
    def __init__(self, cookies, ua, args):
        self.cookies = cookies
        self.ua = ua
        self.total = 3000
        self.per_page = args.per_page
        if args.include_managers:
            self.uri = 'https://crowdin.com/project_actions/members_list'
        else:
            self.uri = 'https://crowdin.com/group_actions/members_list'

    def __iter__(self):
        self.cur_page = 0
        return self

    def __next__(self):
        if self.cur_page * self.per_page > self.total:
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
                'rp': self.per_page,
                'filter': '',
                'request': 1
            }
        headers = {
                'referer': 'http://translate.lineageos.org/project/lineageos/translators',
                'x-csrf-token': self.cookies['csrf_token'],
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
        self.headers = {
                'referer': 'http://translate.lineageos.org/project/lineageos/translators',
                'x-csrf-token': self.cookies['csrf_token'],
                'user-agent': self.ua,
                'x-requested-with': 'XMLHttpRequest',
        }

    def get(self):
        uri = 'http://translate.lineageos.org/project_actions/translator_info'
        r = requests.get(uri, cookies=self.cookies, params=self.params, headers=self.headers)
        #print(json.dumps(r.json()))
        return r.json()['data']

    def remove(self):
        uri = 'https://crowdin.com/project_actions/remove_user_from_project'
        r = requests.get(uri, cookies=self.cookies, params=self.params, headers=self.headers)
        #print(json.dumps(r.json()))
        return r.json()
