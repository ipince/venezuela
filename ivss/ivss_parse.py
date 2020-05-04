#!/usr/bin/python

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
  keys = ['id', 'nationality', 'name', 'affiliation_date', 'status', 'weeks', 'company_id', 'company_name', 'company_start_date', 'company_end_date', 'verification_code', 'scrape_status', 'scrape_timestamp_utc']
  with open(filename, 'wb') as outfile:
    writer = csv.DictWriter(outfile, keys)
    writer.writeheader()
    writer.writerows(lines)

def convert_date(d):
  # Convert from D/M/YYYY to YYYY-MM-DD (string)
  parts = d.split('/')
  return '-'.join([parts[2], parts[1].zfill(2), parts[0].zfill(2)])

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

  if output['affiliation_date']:
    output['affiliation_date'] = convert_date(output['affiliation_date'])

  company_date = output['company_date']
  if 'egreso' in company_date:
    output['company_start_date'] = ''
    d = company_date.replace('fecha de egreso ', '')
    output['company_end_date'] = convert_date(d)
  elif 'ingreso' in company_date:
    d = company_date.replace('fecha de ingreso ', '')
    output['company_start_date'] = convert_date(d)
    output['company_end_date'] = ''
  del output["company_date"]

  if output['verification_code'] == 'null':
    del output['verification_code']

  return output

def process_cedula(cedula, root, skip=False):
  print 'Processing id ' + str(cedula)
  output = {}

  filepath = ivss_utils.path(cedula[1], root)
  try:
    content = read(filepath)
  except IOError, e:
    if skip: # print error and continue
      print "  Could not find file (%s) for cedula %s" % (filepath, cedula)
      return output
    else:
      raise e

  output['id'] = cedula[1]
  output['nationality'] = cedula[0]
  output['scrape_timestamp_utc'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getmtime(filepath)))

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
      cedulas.append(('V', cedula))  # Assume V for dir walks
  return cedulas


if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option("-i", "--input", dest="input", type="str")
  parser.add_option("-d", "--dir", dest="dir", type="str")
  parser.add_option("-s", "--skip", dest="skip", action="store_true", help="If true, skip over records in <input> that are not found in <dir>")
  (options, args) = parser.parse_args()

  if not options.input and not options.dir:
    parser.error("Must pass in an input file or a cache directory to process")

  if options.input:
    cedulas = ivss_utils.read_batch(options.input)
  else:
    cedulas = walk(options.dir)

  lines = []
  for cedula in cedulas:
    data = process_cedula(cedula, options.dir, skip=options.skip)
    if data: # skip empty records
      lines.append(data)

  outfile = options.input if options.input else options.dir
  outfile = outfile.replace("/", "")
  write_csv(lines, outfile + '.csv')
