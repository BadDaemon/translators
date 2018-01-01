from __future__ import print_function
import codecs
import sys
import json

from collections import OrderedDict

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

f = codecs.open('proofreaders.json', 'r', 'utf-8-sig')
jsonData = json.load(f, object_pairs_hook=OrderedDict)
f.close()

if not 'managers' in jsonData or \
    not 'global_proofreaders' in jsonData or \
    not 'languages' in jsonData:
        print('No valid input file!')
        exit()

for group in jsonData:
    if not group == 'managers' and not group == 'global_proofreaders': continue
    print("{}:".format(group))
    for m in sorted(jsonData[group]):
        s = m.split(" (")
        if len(s) == 2:
            name = s[0]
            nick = s[1][:-1]
        else:
            name = m
            nick = m
        print("    - name: {}".format(name))
        print("      nick: {}".format(nick))


# ---------------- language specific proofreaders ----------------

languages = jsonData['languages']
# add these manually because they are managers and wouldn't appear in the list of proofreaders
# otherwise
additionalProofreaders = {}
additionalProofreaders["Italian"] = ['Joey Rizzoli (linuxx)']
additionalProofreaders["German"] = ['Michael W (BadDaemon)']
additionalProofreaders["Greek"] = ['Michael Bestas (mikeioannina)']
additionalProofreaders["Russian"] = ['Vladislav Koldobskiy (NeverGone)']

languages = merge_two_dicts(languages, additionalProofreaders)
print('languages:')
for language in sorted(languages):
    print('    - name: {}'.format(language))
    print('      proofreaders: {}'.format(languages[language]))
