#!/usr/bin/python
# -*- coding: UTF-8 -*-

import argparse
import csv
import glob
import HTMLParser
import os
import sys

from lxml import etree


arg_parser = argparse.ArgumentParser(
                 description='Dumps information from scraped CNE html files into csv format')
arg_parser.add_argument('root_dir', help='The directory the html files are stored in')
arg_parser.add_argument('--millions', '-m', nargs='?', type=str, required=True,
                        help='Millionths regexp')
arg_parser.add_argument('--thousands', '-t', nargs='?', type=str, default='*',
                        help='Thousandths regexp')
arg_parser.add_argument('--cedula', '-c', nargs='?', type=str, default='*',
                        help='Cedula filter to use on the filename')
arg_parser.add_argument('--prefix', '-p', nargs='?', type=int,
                        help='A prefix to restrict the dump on')
args = arg_parser.parse_args()

print args
directory = args.root_dir

#prefix = args.prefix
#mils, thous, ones = '*', '*', '*'

#if prefix and 0 <= prefix <= 30000000:
#  if 0 <= prefix < 100:
#    mils = str(prefix)
#  elif 100 <= prefix < 100000:
#    mils = str(prefix)[0:2]
#    thous = str(prefix)[2:]
#  elif 100000 <= prefix:
#    mils = str(prefix)[0:2]
#    thous = str(prefix)[2:]
#    ones = prefix - ((prefix / 1000000) * 100000)
#else:
#  print "No prefix specified, or not a number, or too long: '%s'. Exiting" % prefix
#  exit()

#print "mils: %s, thous: %s, ones: %s, prefix: %d" % (mils,thous,ones,prefix)

# If there is no thousands filter, go over directories manually to avoid over-sorting
# Going over thousands dirs first speeds up things mildly.
html_files = list()
thousands_dirs = glob.glob(os.path.join(directory, args.millions, args.thousands))
for d in sorted(thousands_dirs):
  html_files.extend(sorted(glob.glob(os.path.join(d, 'web_registro*cedula=' + args.cedula))))
print len(html_files)
exit()


def read(filename):
  print "Reading " + filename
  f = open(filename, 'r')
  return f.read()
  #return extract_from_html(etree.HTML(contents))

# REMOVE begin
def extract_from_html(tree):
  #for elm in tree.xpath('//font[@color="#00387b"]'):
  for elm in tree.xpath('//table[@cellpadding="5"]//td'):
    print "OK"
    print elm.text
    print elm.attrib
    return elm

#/html/body/table/tbody/tr/td/table/tbody/tr[5]/td/table[1]/tbody/tr[3]/td/table/tbody/tr[2]/td[1]/text()
# REMOVE end

keys = ['cedula', 'full_name', 'first_name', 'second_name', 'first_surname', 'second_surname',
        'voting', 'state', 'muni', 'parish', 'center', 'table', 'center_address', 'table_member',
        'cne_date', 'scrape_date']

class CneHtmlParser(HTMLParser.HTMLParser):
  def __init__(self):
    HTMLParser.HTMLParser.__init__(self)
    self.ignored_keys = [
      'REGISTRO ELECTORAL - Consulta de Datos',
      'DATOS PERSONALES',
      'DATOS DEL ELECTOR',
      u'Conoce los Miembros de Mesa de tu Centro de Votación.'.encode('utf-8'),
      'SERVICIO ELECTORAL',
      'Planilla de Reclamo y Registro de Fallecidos',
      'Instructivo para llenar la Planilla de Reclamo y Registro de Fallecidos',
      'RECOMENDACIONES',
      'ESTATUS',
      u'Si ha realizado alguna solicitud recientemente, se recuerda que la actualización de sus datos se efectúa mensualmente, por lo que se le invita a realizar nuevamente la consulta luego de un (01) mes de haber solicitado su inscripción.'.encode('utf-8'),
      u'Si usted aun no ha realizado una solicitud se le invita a inscribirse en los Centros de Actualización más cercanos a su residencia.'.encode('utf-8'),
      'Imprimir',
      'Cerrar']
    self.mapping_keys = {
      u'Cédula:'.encode('utf-8'): keys[0],
      'Nombre:': keys[1],
      'Primer Nombre:': keys[2],
      'Segundo Nombre:': keys[3],
      'Primer Apellido:': keys[4],
      'Segundo Apellido:': keys[5],
      'Estado:': keys[7],
      'Municipio:': keys[8],
      'Parroquia:': keys[9],
      'Centro:': keys[10],
      'Mesa:': keys[11],
      u'Dirección:'.encode('utf-8'): keys[12],
    }
    self.boolean_keys = {
      u'Esta cédula de identidad no se encuentra inscrito en el Registro Electoral.'.encode('utf-8'): (keys[6], False),
      u'Usted está habilitado para sufragar en las Elecciones Regionales del 16 de Diciembre de 2012'.encode('utf-8'): (keys[6], True),
      'Usted NO fue seleccionado para prestar el Servicio Electoral, Elecciones 2012': (keys[13], False),
      'Registro Electoral correspondiente al 15 de Abril de 2012.': (keys[14], 'abril 15, 2012'),
    }
    self.reset()

  def reset(self):
    HTMLParser.HTMLParser.reset(self)
    self.tds = 0
    self.current_key = None
    self.output = {}

  def handle_data(self, data):
    data = data.strip()
    if not data or data in self.ignored_keys:
      return # ignore

    if data in self.boolean_keys:
      self.output[self.boolean_keys[data][0]] = self.boolean_keys[data][1]
      self.current_key = None
      return

    if data in self.mapping_keys:
      self.current_key = data
    elif self.current_key:
      self.output[self.mapping_keys[self.current_key]] = data
      self.current_key = None
    else:
      print "Found data: ", data, ", ", type(data)

parser = CneHtmlParser()

html_files = sorted(glob.glob(directory + "/*"))

out_file = open('out.csv', 'wb')
writer = csv.DictWriter(out_file, keys)
writer.writeheader()

for i in range(1, 1000):
  print ""
  parser.feed(read(html_files[i]))
  print parser.output
  writer.writerow(parser.output)
  parser.close()
  parser.reset()
  #extract_from_file(html_files[i])
