#!/usr/bin/python

import os
import requests
import time
import random

from optparse import OptionParser
from HTMLParser import HTMLParser

SLEEP_TIME_SEC = 3
HTML = HTMLParser()
DUMMY_RESPONSE_CONTENT = 'dummy content'

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

def read_batch(filepath):
  with open(filepath, 'r') as f:
    return f.read().splitlines()

def scrape_randomly(beg, end, force=False, dry_run=True):
  cedulas = range(beg, end)
  scrape(cedulas, directory, force=force, dry_run=dry_run)
 
def scrape(cedulas, directory, force=False, dry_run=True):
  # randomize
  random.shuffle(cedulas)
  directory = directory if not dry_run else directory + '-dummy'
  for cedula in cedulas:
    # check if already fetched.
    filepath = path(cedula, directory)
    if os.path.exists(filepath) and not force:
      print "Reading from cached file: %s" % filepath
      #contents = file(filepath).read()
    else:
      contents = fetch(cedula, filepath, dry_run=dry_run)
    #print contents

def fetch(cedula, filepath, sleep=SLEEP_TIME_SEC, dry_run=True):
  URL = 'http://www.ivss.gob.ve:28088/ConstanciaCotizacion/BuscaCotizacionCTRL'

  print "Fetching: " + str(cedula)

  form = {'consultar': 'Buscar', 'nacionalidad': 'V', 'cedula': cedula }
  start = time.time()
  if dry_run:
    response = DUMMY_RESPONSE_CONTENT
  else:
    response = requests.post(URL, form).text
  elapsed = time.time() - start
  print "Took %.2fs" % elapsed

  outfile = file(filepath, 'w')
  response = HTML.unescape(response)
  outfile.write(response.encode('utf8'))
  time.sleep(sleep)
  return response

if __name__ == '__main__':
  parser = OptionParser()
  #parser.add_option("-m", "--millions", dest="millions", type="int")
  parser.add_option("-b", "--beg", dest="beginning", type="int")
  parser.add_option("-e", "--end", dest="end", type="int")
  parser.add_option("-f", "--force", dest="force", action="store_true")
  parser.add_option("-d", "--dry_run", dest="dry_run", action="store_true")
  parser.add_option("-i", "--input", dest="input_file", type="str")
  (options, args) = parser.parse_args()

  if not options.input_file:
    if options.beginning is None or options.end is None or options.beginning > options.end:
      parser.error("-b, and -e must be specified and 'end' must be larger than 'beg'")

  if options.input_file:
    first = options.input_file.split(".")[0]
    cedulas = read_batch(options.input_file)
    scrape(cedulas, first, force=options.force, dry_run=options.dry_run)
  else:
    scrape(options.beginning, options.end, 'cache', force=options.force, dry_run=options.dry_run)
