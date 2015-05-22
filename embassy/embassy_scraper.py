#!/usr/bin/python

user_email = 'juancam64@hotmail.com'
user_pass = '6288513'

types = [
    'pasaporte',
    'cadivi',
    'fedevida',
    'acpension',
    'certuso',
    ]

def build_link(kind):
  return 'http://tramites.embavenez-us.org/' + kind + '/planillapdf/id/'


