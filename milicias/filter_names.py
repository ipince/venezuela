#!/usr/bin/python

import csv
# go to venezuela/rep. do PYTHONPATH=`pwd`:$PYTHONPATH
import db
import re

# sudo pip install python-Levenshtein
from Levenshtein import distance


# assumes len(names1) = len(names2) + 1
def check_perms(names1, names2):
  # try removing one until distance is low enough
  for name in names1:
    spliced = filter(lambda n: n != name, names1)
    if distance(' '.join(spliced), ' '.join(names2)) <= thres:
      #print 'YAY, found match by trying permutations! (%s, %s)' % (' '.join(spliced), ' '.join(names2))
      return True
  return False


input_csv = open('milicias-merged-raw.csv', 'rb')
csv_reader = csv.DictReader(input_csv)

output_csv = open('milicias-merged-cleaned.csv', 'wb')
csv_writer = csv.DictWriter(output_csv, csv_reader.fieldnames)
csv_writer.writeheader()

d = db.DB('venezuela', 'venepass', 'venedb')

count = 0
not_matched = 0
not_found = 0
dist_sum = 0
thres = 6
unmatched = list()

for row in csv_reader:
  count += 1

  # clean cedulas
  row['Cedula'] = row['Cedula'].replace('.', '')

  cedula = row['Cedula']
  csv_names = sorted(re.split('\W+', row['Nombre'].lower()))
  result = d.select_person(cedula)
  if len(result) == 0:
    print "NOT FOUND: " + repr(row)
    not_found += 1
    continue

  db_names = sorted(filter(lambda x: x, result[0][1:]))
  if len(csv_names) > len(db_names):
    if check_perms(csv_names, db_names):
      csv_writer.writerow(row)
      continue
  elif len(db_names) > len(csv_names):
    if check_perms(db_names, csv_names):
      csv_writer.writerow(row)
      continue

  # lengths are the same
  csv_name = ' '.join(csv_names)
  db_name = ' '.join(db_names)
  dist = distance(csv_name, db_name)

  if dist > thres:
    # try matching pairs of names
    num_matches = 0
    for name in csv_names:
      if name in db_names:
        num_matches += 1

    if num_matches >= 2:
      #print 'MATCHED based on per-word matches: (%s, %s)' % (csv_name, db_name)
      csv_writer.writerow(row)
      continue

    # if we get here, we've failed.
    row['db_name'] = db_name
    unmatched.append(row)
    not_matched += 1
    dist_sum += dist
#    print '%s -> (%s, %s), diff %d' % (cedula, csv_name, db_name, dist)
  else: # dist is below threshold (we have a match)
    csv_writer.writerow(row)



print 'iterated %d times' % count
print 'not matched: %d' % not_matched
print 'avg dist for non-matches: %d' % (float(dist_sum) / not_matched)
print 'not found: %d' % not_found

for r in sorted(unmatched, key=lambda d: d['Fecha']):
  print r
