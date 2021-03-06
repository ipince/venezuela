#!/usr/bin/python

import os
import requests
import time
import random

from optparse import OptionParser
from HTMLParser import HTMLParser

import ivss_utils

SLEEP_TIME_SEC = 2
HTML = HTMLParser()
DUMMY_RESPONSE_CONTENT = 'dummy content'

def scrape_randomly(beg, end, directory, known=None, wait=None, force=False, dry_run=True):
  skip = set()
  if known:
    skip.update(ivss_utils.read_batch(known))
  print "found %s ids in skip file" % len(skip)
  cedulas = [('V', x) for x in range(beg, end) if ('V', x) not in skip]
  scrape(cedulas, directory, wait=wait, force=force, dry_run=dry_run)
 
def scrape(cedulas, directory, wait=None, force=False, dry_run=True):
  # randomize
  random.shuffle(cedulas)
  directory = directory + '-cache' if not dry_run else directory + '-dummy'
  for cedula in cedulas:
    # check if already fetched.
    filepath = ivss_utils.path(cedula[1], directory)
    if os.path.exists(filepath) and not force:
      print "Reading from cached file: %s" % filepath
      #contents = file(filepath).read()
    else:
      contents = fetch(cedula, filepath, sleep=wait, dry_run=dry_run)
    #print contents

def fetch(cedula, filepath, sleep=None, dry_run=True):
  URL = 'http://www.ivss.gob.ve:28088/ConstanciaCotizacion/BuscaCotizacionCTRL'

  print "Fetching: " + str(cedula)

  form = {'consultar': 'Buscar', 'nacionalidad': cedula[0], 'cedula': cedula[1] }
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

  # Back off if the request took too long.
  if elapsed > 6:
    time.sleep(20)
  time.sleep(sleep if sleep else SLEEP_TIME_SEC)
  return response

if __name__ == '__main__':
  parser = OptionParser()
  #parser.add_option("-m", "--millions", dest="millions", type="int")
  parser.add_option("-b", "--beg", dest="beginning", type="int")
  parser.add_option("-e", "--end", dest="end", type="int")
  parser.add_option("-f", "--force", dest="force", action="store_true")
  parser.add_option("-d", "--dry_run", dest="dry_run", action="store_true")
  parser.add_option("-i", "--input", dest="input_file", type="str")
  parser.add_option("-k", "--known", dest="known", type="str")
  parser.add_option("-w", "--wait", dest="wait", type="int")
  (options, args) = parser.parse_args()

  if not options.input_file:
    if options.beginning is None or options.end is None or options.beginning > options.end:
      parser.error("-b, and -e must be specified and 'end' must be larger than 'beg'")

  if options.input_file:
    cedulas = ivss_utils.read_batch(options.input_file)
    scrape(cedulas, options.input_file, wait=options.wait, force=options.force, dry_run=options.dry_run)
  else:
    scrape_randomly(options.beginning, options.end, 'seq', known=options.known, wait=options.wait, force=options.force, dry_run=options.dry_run)
