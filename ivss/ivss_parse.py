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

# TODO:
# - parse date properly
# - extract nationality
# - read from correct dir

import os
import time
import csv

import ivss_utils

from optparse import OptionParser
from lxml import etree as ET

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

def read(filepath):
  with open(filepath, 'r') as f:
    return f.read()

def write_csv(lines, filename):
  keys = ['id', 'name', 'affiliation_date', 'status', 'weeks', 'company_id', 'company_name', 'company_start_date', 'company_end_date', 'verification_code', 'scrape_status', 'scrape_timestamp_utc']
  with open(filename, 'wb') as outfile:
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

def process_cedula(cedula, root):
  print 'Processing id ' + str(cedula)
  filepath = ivs_utils.path(cedula, root)
  output = {}
  output['id'] = cedula
  output['scrape_timestamp_utc'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getmtime(filepath)))

  content = read(filepath)
  if not content:
    output['scrape_status'] = 'blank_page'
    return output
  elif 'no tiene Semanas Cotizadas' in content:
    output['weeks'] = 0
    output['scrape_status'] = 'no_weeks'
    return output
  elif 'es incorrecta' in content:
    output['scrape_status'] = 'not_found'
    return output

  tree = ET.HTML(content)
  extract(tree, output)
  output['scrape_status'] = 'success'

  return output

def walk(root):
  cedulas = []
  for dir, subdirs, files in os.walk(root):
    prefix = ''.join(dir.split('/')[1:])
    for filename in files:
      suffix = filename.split('.')[0]
      cedula = int(prefix + suffix)
      cedulas.append(cedula)
  return cedulas


if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option("-b", "--batch", dest="batch", type="str")
  parser.add_option("-d", "--dir", dest="dir", type="str")
  (options, args) = parser.parse_args()

  if not options.batch and not options.dir:
    parser.error("Must pass in a batch to process, either by batch name (-b) or by root dir (-d)")
  if options.batch and options.dir:
    parser.error("")

  # Find list of input.
  root = options.batch if options.batch else options.dir
  cedulas = ivss_utils.read_batch(root + '.txt') if options.batch else walk(root)
  lines = []

  for cedula in cedulas:
    lines.append(process_cedula(cedula, root))

  write_csv(lines, root + '.csv')
