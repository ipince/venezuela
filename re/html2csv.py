#!/usr/bin/python
# -*- coding: UTF-8 -*-

import csv
import glob
import HTMLParser
import sys

from lxml import etree

print "args are " + repr(sys.argv)

directory = sys.argv[1]


def read(filename):
  print "Reading " + filename
  f = open(filename, 'r')
  return f.read()
  #return extract_from_html(etree.HTML(contents))

def extract_from_html(tree):
  #for elm in tree.xpath('//font[@color="#00387b"]'):
  for elm in tree.xpath('//table[@cellpadding="5"]//td'):
    print "OK"
    print elm.text
    print elm.attrib
    return elm

#/html/body/table/tbody/tr/td/table/tbody/tr[5]/td/table[1]/tbody/tr[3]/td/table/tbody/tr[2]/td[1]/text()

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
      u'Cédula:'.encode('utf-8'): 'cedula',
      'Nombre:': 'nombre_completo',
      'Primer Nombre:': 'primer_nombre',
      'Segundo Nombre:': 'segundo_nombre',
      'Primer Apellido:': 'primer_apellido',
      'Segundo Apellido:': 'segundo_apellido',
      'Estado:': 'estado',
      'Municipio:': 'municipio',
      'Parroquia:': 'parroquia',
      'Centro:': 'centro',
      'Mesa:': 'mesa',
      u'Dirección:'.encode('utf-8'): 'direccion_centro',
    }
    self.boolean_keys = {
      u'Esta cédula de identidad no se encuentra inscrito en el Registro Electoral.'.encode('utf-8'): ('registrado', False),
      u'Usted está habilitado para sufragar en las Elecciones Regionales del 16 de Diciembre de 2012'.encode('utf-8'): ('registrado', True),
      'Usted NO fue seleccionado para prestar el Servicio Electoral, Elecciones 2012': ('miembro_mesa', False),
      'Registro Electoral correspondiente al 15 de Abril de 2012.': ('fecha_cne', 'abril 15, 2012'),
    }
    self.reset()

  def reset(self):
    HTMLParser.HTMLParser.reset(self)
    self.tds = 0
    self.current_key = None
    self.output = {}

  def handle_starttag(self, tag, attributes):
    if tag == 'td':
      self.tds += 1

  def handle_endtag(self, tag):
    if tag == 'td': self.tds -= 1
    if self.tds < 0:
      print "WARNING: tds less than 0 (%d). Resetting" % self.tds
      self.tds = 0

  def handle_data(self, data):
    if self.tds <= 0:
      return

#    print "Found data: ", data, ", ", type(data)

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

html_files = glob.glob(directory + "/*")

for i in range(1, 100):
  print ""
  parser.feed(read(html_files[i]))
  print parser.output
  if 'segundo_apellido' in parser.output: print parser.output['segundo_apellido']
  parser.close()
  parser.reset()
  #extract_from_file(html_files[i])
