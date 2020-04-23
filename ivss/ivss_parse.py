#!/usr/bin/python

# Takes the output of the IVSS and extracts the following data:
# id
# name
# weeks
# status
# company_name
# company_id
# start_date
# end_date
# verification code
# timestamp

import os
import time
import csv

from lxml import etree as ET

def read(filepath):
  with open(filepath, 'r') as f:
    return f.read()

def read_batch(filepath):
  with open(filepath, 'r') as f:
    return f.read().splitlines()

# parse html
# run xpath queries

XPATH_NAME = '/html/body/form/table[3]/iterator/tr[1]/td/p/b[2]'
XPATH_WEEKS = '/html/body/form/table[3]/iterator/tr[1]/td/p/b[4]'
XPATH_AFFILIATION_DATE = '/html/body/form/table[3]/iterator/tr[1]/td/p/b[6]'
XPATH_STATUS = '/html/body/form/table[3]/iterator/tr[1]/td/p/b[7]'
XPATH_COMPANY_NAME = '/html/body/form/table[3]/iterator/tr[1]/td/p/b[8]'
XPATH_COMPANY_ID = '/html/body/form/table[3]/iterator/tr[1]/td/p/b[9]'
XPATH_COMPANY_DATE = '/html/body/form/table[3]/iterator/tr[1]/td/p/b[10]'
XPATH_CODE = '/html/body/form/table[3]/iterator/tr[8]/td/b'

XPATHS = {
  'name': XPATH_NAME,
  'weeks': XPATH_WEEKS,
  'affiliation_date': XPATH_AFFILIATION_DATE,
  'status': XPATH_STATUS,
  'company_name': XPATH_COMPANY_NAME,
  'company_id': XPATH_COMPANY_ID,
  'company_date': XPATH_COMPANY_DATE,
  'verification_code': XPATH_CODE
}


def path(cedula, toplevel):
  # structure is cache/<2-digit-millions>/<3-digit-thousands>
  filled = str(cedula).zfill(9)
  millions_path = os.path.join(toplevel, filled[:3])
  thousands_path = os.path.join(millions_path, filled[3:6])
  if not os.path.exists(millions_path):
    os.makedirs(millions_path)
  if not os.path.exists(thousands_path):
    os.makedirs(thousands_path)
  return os.path.join(thousands_path, filled[6:] + '.html')

def write_csv(lines):
  keys = ['id', 'name', 'affiliation_date', 'status', 'weeks', 'company_id', 'company_name', 'company_start_date', 'company_end_date', 'verification_code', 'scrape_status', 'scrape_timestamp_utc']
  with open('batch2.csv', 'wb') as outfile:
    writer = csv.DictWriter(outfile, keys)
    writer.writeheader()
    writer.writerows(lines)

def extract(tree, output):
  for key in XPATHS:
    results = tree.xpath(XPATHS[key])
    if results:
      if len(results) == 1:
        output[key] = results[0].text.strip().encode('utf8')
      else:
        print 'Found more than 1 result'
        for r in results:
          print '  ', r.tag, r.attrib, r.text
    else:
      print 'Did not find results for xpath: ' + XPATHS[key]

  # clean some of the keys
  output['weeks'] = int(output['weeks'].replace(' semanas cotizadas', ''))
  company_date = output['company_date']
  if 'egreso' in company_date:
    output['company_start_date'] = ''
    output['company_end_date'] = company_date.replace('fecha de egreso ', '')
  elif 'ingreso' in company_date:
    output['company_start_date'] = company_date.replace('fecha de ingreso ', '')
    output['company_end_date'] = ''
  del output["company_date"]

  return output

lines = []

cedulas = read_batch('batch2.txt')
#cedulas = [3765654]
for cedula in cedulas:
  print 'Processing id ' + str(cedula)
  filepath = path(cedula, 'cache')
  output = {}
  output['id'] = cedula
  output['scrape_timestamp_utc'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getmtime(filepath)))

  content = read(filepath)
  if 'no tiene Semanas Cotizadas' in content:
    output['weeks'] = 0
    output['scrape_status'] = 'no_weeks'
    lines.append(output)
    continue
  elif 'es incorrecta' in content:
    output['scrape_status'] = 'not_found'
    lines.append(output)
    continue

  tree = ET.HTML(content)

  extract(tree, output)
  output['scrape_status'] = 'success'
  lines.append(output)

#print lines

write_csv(lines)

