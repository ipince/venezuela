#!/usr/bin/python

import csv

from collections import defaultdict

debug = False

indeces_14a = {
  'state_code': 0,
  'state_name': 1,
  'center_code_old': 8,
  'center_code_new': 9,
  'center_name': 6,
  'table': 10,

  'voters': 21,
  'scrut_votes': 18,
  'valid_votes': 19,
  'null_votes': 17,
  'abstention': 20,
  
  'maduro': 11,
  'capriles': 12,
}

def add_votes(totals, row, indeces):
  totals['scrutinized'] += int(row[indeces['scrut_votes']])
  totals['valid'] += int(row[indeces['valid_votes']])
  totals['null'] += int(row[indeces['null_votes']])
  totals['maduro'] += int(row[indeces['maduro']])
  totals['capriles'] += int(row[indeces['capriles']])
  try:
    totals['voters'] += int(row[indeces['voters']])
  except ValueError:
    if debug: print row

def rounded_pct(num, den):
  return int(round(100 * float(num) / float(den)))

def process_csv(indeces):
  csv_file = open('esdata_resultados_elecc_2013-04-14-v1_2.csv', 'rb')
  csv_reader = csv.reader(csv_file)

  totals = defaultdict(int)
  states = {}
  centers = {}
  tables = {}

  itr = 1
  first_row = True
  num_ignored = 0
  for row in csv_reader:
    if first_row:
      print "Header is: " + repr(row)
      first_row = False
      continue  # skip header row

    if row[indeces['state_code']] == '' or row[indeces['state_code']] == '99': # null and Embajadas
      print "Ignoring: " + repr(row)
      num_ignored += 1
      continue

    # add to grand totals
    add_votes(totals, row, indeces)
    # aggregate by state
    state_code = str.zfill(row[indeces['state_code']], 2)
    if state_code not in states:
      states[state_code] = defaultdict(int)
      states[state_code]['name'] = row[indeces['state_name']]
    add_votes(states[state_code], row, indeces)

    # aggregate by center
    center_code = str.zfill(row[indeces['center_code_new']], 9)
    if center_code not in centers:
      centers[center_code] = defaultdict(int)
      centers[center_code]['name'] = row[indeces['center_name']]
    add_votes(centers[center_code], row, indeces)
    itr += 1

    # aggregate by table
    table_code = center_code + "." + row[indeces['table']]
    if table_code not in tables:
      tables[table_code] = defaultdict(int)
      tables[table_code]['name'] = row[indeces['center_name']] + "-" + row[indeces['table']]
    add_votes(tables[table_code], row, indeces)

  # calculate participation rates
  for state in states:
    states[state]['particip'] = rounded_pct(states[state]['scrutinized'], states[state]['voters'])
  for code in tables:
    tables[code]['particip'] = rounded_pct(tables[code]['scrutinized'], tables[code]['voters'])

  print "Done aggregating. Ignored %d rows" % num_ignored
  return [totals, states, centers, tables]


[totals, states, centers, tables] = process_csv(indeces_14a)

print totals
for state in states:
  print state + ": " + repr(states[state])


print "num centers: " + str(len(centers))

print "Center with no scrutinized votes:"
for code in centers:
  if centers[code]['scrutinized'] == 0:
    print code + ": " + repr(centers[code])

print "Capriles got 0 votes in the following centers:"
count = 0
for code in centers:
  if centers[code]['capriles'] == 0 and centers[code]['scrutinized'] != 0:
    print code + ": " + repr(centers[code])
    count += 1
print "Total of %d centers" % count

print "Capriles got 0 votes in the following tables:"
count = 0
for code in tables:
  if tables[code]['capriles'] == 0 and tables[code]['scrutinized'] != 0:
    print code + ": " + repr(tables[code])
    count += 1
print "Total of %d tables" % count

print "Maduro got 0 votes in the following tables:"
for code in tables:
  if tables[code]['maduro'] == 0 and tables[code]['scrutinized'] != 0:
    print code + ": " + repr(tables[code])


