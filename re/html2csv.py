#!/usr/bin/python

import csv
import glob
import sys

from lxml import etree

print "args are " + repr(sys.argv)

#directory = sys.argv[1]

def extract_from_file(filename):
  print "Reading " + filename
  f = open(filename, 'r')
  contents = f.read()
  return extract_from_html(etree.HTML(contents))

def extract_from_html(tree):
  #for elm in tree.xpath('//font[@color="#00387b"]'):
  for elm in tree.xpath('//table[@cellpadding="5"]//td'):
    print "OK"
    print elm.text
    print elm.attrib
    return elm

#/html/body/table/tbody/tr/td/table/tbody/tr[5]/td/table[1]/tbody/tr[3]/td/table/tbody/tr[2]/td[1]/text()
#html_files = glob.glob(directory + "/*")

#for i in range(1, 10):
#  print "NEW ONE ============="
#  extract_from_file(html_files[i])


