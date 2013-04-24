#!/usr/bin/python

import csv

from collections import defaultdict

debug = False

STATE_CODE_IDX = 0
STATE_NAME_IDX = 1
CENTER_CODE_OLD_IDX = 8
CENTER_CODE_NEW_IDX = 9
CENTER_NAME_IDX = 6
TABLE_IDX = 10

SCRUT_VOTES_IDX = 18
VALID_VOTES_IDX = 19
NULL_VOTES_IDX = 17
MADURO_IDX = 11
CAPRILES_IDX = 12

ABSTENTION_IDX = 20
BOOK_TOTAL_IDX = 21

def add_votes(totals, row):
  totals['scrutinized'] += int(row[SCRUT_VOTES_IDX])
  totals['valid'] += int(row[VALID_VOTES_IDX])
  totals['null'] += int(row[NULL_VOTES_IDX])
  totals['maduro'] += int(row[MADURO_IDX])
  totals['capriles'] += int(row[CAPRILES_IDX])
  try:
    totals['voters'] += int(row[BOOK_TOTAL_IDX])
  except ValueError:
    if debug: print row

def rounded_pct(num, den):
  return int(100 * float(num) / float(den))

def process_csv():
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

    if row[STATE_CODE_IDX] == '' or row[STATE_CODE_IDX] == '99': # null and Embajadas
      print "Ignoring: " + repr(row)
      num_ignored += 1
      continue

    # add to grand totals
    add_votes(totals, row)
    # aggregate by state
    state_code = str.zfill(row[STATE_CODE_IDX], 2)
    if state_code not in states:
      states[state_code] = defaultdict(int)
      states[state_code]['name'] = row[STATE_NAME_IDX]
    add_votes(states[state_code], row)

    # aggregate by center
    center_code = str.zfill(row[CENTER_CODE_NEW_IDX], 9)
    if center_code not in centers:
      centers[center_code] = defaultdict(int)
      centers[center_code]['name'] = row[CENTER_NAME_IDX]
    add_votes(centers[center_code], row)
    itr += 1

    # aggregate by table
    table_code = center_code + "." + row[TABLE_IDX]
    if table_code not in tables:
      tables[table_code] = defaultdict(int)
      tables[table_code]['name'] = row[CENTER_NAME_IDX] + "-" + row[TABLE_IDX]
    add_votes(tables[table_code], row)

  # calculate participation rates
  for state in states:
    states[state]['particip'] = rounded_pct(states[state]['scrutinized'], states[state]['voters'])
  for code in tables:
    tables[code]['particip'] = rounded_pct(tables[code]['scrutinized'], tables[code]['voters'])

  print "Done aggregating. Ignored %d rows" % num_ignored
  return [totals, states, centers, tables]


[totals, states, centers, tables] = process_csv()

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


