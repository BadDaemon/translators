import json

try:
  f = open('languages.json', 'r', )
  jsonData = json.load(f)
  f.close()
except Exception as e:
  print(e)

def getLanguages():
  languages = {}
  for language in jsonData[0]['data']:
    languages[language['id']] = language['title']
  return languages

