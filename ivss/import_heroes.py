#!/usr/bin/python

import requests
import json
import csv
import re
import time
import os
import sys

from HTMLParser import HTMLParser

html = HTMLParser()


def fetch_all():
  URL = 'https://apivqjgrhp7f7x5.gobve.net/endpoints/verifications-summary'
  params = {'access': '4yeZ6Wecx2ZSXfAY7NVfzMhQtHaHkPgYXnQU9FWh', 'limit': 100}
  headers = {'x-api-key': 'OzutJZwPsUbrnoBzZNtK7jPzsR5jclS6FWvxX5Y3'}
  for page in xrange(366, 1000):
    print 'Fetching page %s...' % (page)
    params['page'] = page
    response = requests.get(URL, params=params, headers=headers)
    cleaned = html.unescape(response.text)
    cleaned = re.sub('\s+', ' ', cleaned)
    out = file('cache/' + str(page) + '.json', 'wb')
    out.write(cleaned.encode('utf8'))

    parsed = json.loads(cleaned)
    if len(parsed['data']) < 1:
      print 'Finished scrape!'
    time.sleep(3)

def load():
  with open('tmp.txt', 'r') as f:
    return f.read()


def dump_local_files(root='cache'):
  candidates = []
  documents = []

  for dir, subdirs, files in os.walk(root):
    prefix = ''.join(dir.split('/')[1:])
    for filename in files:
      with open(os.path.join(root, filename), 'r') as f:
        contents = f.read()
        (new_candidates, new_docs) = process_page(contents)
        candidates.extend(new_candidates)
        documents.extend(new_docs)

  # Candidates
  keys = ['id', 'nationality', 'id_full', 'name', 'profession', 'specialty', 'institution_type', 'institution_name', 'institution_dependency', 'institution_municipality', 'institution_state']
  with open('candidates.csv', 'wb') as outfile:
    writer = csv.DictWriter(outfile, keys)
    writer.writeheader()
    for c in candidates:
      writer.writerow({k:v.encode('utf8') for k,v in c.items()})

  # Documents
  keys = ['candidate_id', 'type', 'status', 'different_workplace', 'selected_workplace', 'created', 'id', 'nationality', 'first_name', 'second_name', 'first_surname', 'second_surname']
  with open('documents.csv', 'wb') as outfile:
    writer = csv.DictWriter(outfile, keys)
    writer.writeheader()
    for d in documents:
      writer.writerow({k:v.encode('utf8') if not isinstance(v, int) else v for k,v in d.items()})

def process_page(contents):
  #raw = load()
  #raw2 = re.sub('\s+', ' ', raw)
  contents = contents.replace('\\n', '')
  #records = json.loads(html.unescape(raw2))
  records = json.loads(contents)
  candidates = []
  documents = []
  for c in records['data']:
    for d in c['registerStatus']:
      doc = {}
      doc['candidate_id'] = c['ci'].split('-')[-1]
      doc['type'] = d['documentType']
      doc['status'] = d['status']
      doc['different_workplace'] = d['diferentWorkplace']
      doc['selected_workplace'] = d['selectedWorkplace'].strip()
      doc['created'] = d['createdAt']
      doc['id'] = d['users']['ci']
      doc['nationality'] = d['users']['nationality']
      doc['first_name'] = d['users']['firstName'].strip()
      doc['second_name'] = d['users']['firstName2'].strip()
      doc['first_surname'] = d['users']['lastName'].strip()
      doc['second_surname'] = d['users']['lastName2'].strip()
      documents.append(doc)
    cand = {}
    id_full = c['ci'] 
    cand['id'] = id_full.split('-')[-1]
    cand['nationality'] = '-'.join(id_full.split('-')[:-1])
    cand['id_full'] = id_full
    cand['name'] = c['name'].strip()
    cand['profession'] = c['profession'].strip()
    cand['specialty'] = c['specialtyRegister'].strip()
    cand['institution_type'] = c['institutionType'].strip()
    cand['institution_name'] = c['institutionName'].strip()
    cand['institution_dependency'] = c['institutionalDependency'].strip()
    cand['institution_municipality'] = c['institutionMunicipality'].strip()
    cand['institution_state'] = c['institutionState'].strip()
    candidates.append(cand)
  return (candidates, documents)

#fetch_all()
dump_local_files()
