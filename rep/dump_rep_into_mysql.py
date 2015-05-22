#!/usr/bin/python

import csv
import db

d = db.DB('venezuela', 'venepass', 'venedb')
d.create_tables()

csv_file = open('nacional.csv', 'rb')
csv_reader = csv.DictReader(csv_file, delimiter=';')

count = 0
for row in csv_reader:
  count += 1
  for header in csv_reader.fieldnames:
    if row[header].isspace(): row[header] = None
    else: row[header] = row[header].lower()

  d.save_person(row['cedula'], None,
                row['primer_nombre'],
                row['segundo_nombre'],
                row['primer_apellido'],
                row['segundo_apellido'])

print "Inserted %d rows" % count
