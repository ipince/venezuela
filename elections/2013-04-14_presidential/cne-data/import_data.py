#!/usr/bin/python

import csv
import logging
import utils

from collections import defaultdict

logger = logging.getLogger('log')
logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler())

###
### CSV data processing
###

csv_14a = 'esdata_resultados_elecc_2013-04-14-v1_2.csv'
indices_14a = {
  'state_code': 0,
  'state_name': 1,
  'muni_code': 2,
  'parish_code': 4,
  'center_code_old': 8,
  'center_code_new': 9,
  'center_name': 6,
  'table': 10,

  'voters': 21,
  'scrut_voters': 18, # for 2013, scrut voters == scrut votes
  'scrut_votes': 18,
  'valid_votes': 19,
  'null_votes': 17,
  'abstention': 20,
  
  'gov': 11,
  'cap': 12,
}

csv_7o = 'esdata_resultados_elecc_2012-10-07C.csv'
indices_7o = {
  'state_code': 0,
  'state_name': 1,
  'muni_code': 2,
  'parish_code': 4,
  'center_code_old': 8,
  'center_code_new': 9,
  'center_name': 6,
  'table': 10,

  'scrut_voters': 18,
  'voting_voters': 19,
  'scrut_votes': 21,
  'valid_votes': 22,
  'null_votes': 17,
  'abstention': 20,
  
  'gov': 11,
  'cap': 12,
}

# Merges in voting data from a single CSV row into a dict holding
# running totals for various counts.
def add_votes(totals, row, indices):
  if 'scrut_voters' in indices:
    totals['scrut_voters'] += int(row[indices['scrut_voters']])
  else:
    totals['scrut_voters'] += int(row[indices['scrut_voters']])
  if 'voting_voters' in indices:
    totals['voting_voters'] += int(row[indices['voting_voters']])
  totals['scrut_votes'] += int(row[indices['scrut_votes']])
  totals['valid'] += int(row[indices['valid_votes']])
  totals['null'] += int(row[indices['null_votes']])
  totals['gov'] += int(row[indices['gov']])
  totals['cap'] += int(row[indices['cap']])
  try:
    if 'voters' in indices: totals['voters'] += int(row[indices['voters']])
  except ValueError:
    logger.warning('Invalid number of voters in row: ' + repr(row))

def aggregate_votes(votes, code, row, indices, name_dim=None, name_func=None):
  assert isinstance(votes, dict)
  # Id for the level we're aggregating over
  assert isinstance(code, str)
  if code not in votes:
    votes[code] = defaultdict(int)
    if name_func:
      votes[code]['name'] = name_func(row, indices)
    elif name_dim:
      votes[code]['name'] = row[indices[name_dim]]
  add_votes(votes[code], row, indices)

def process_csv(filename, indices):
  """Returns a dict of dicts:  level -> { id -> count }."""
  csv_file = open(filename, 'rb')
  csv_reader = csv.reader(csv_file)

  totals = defaultdict(int)
  states = {}
  munis = {}
  parishes = {}
  centers = {}
  tables = {}

  first_row = True
  num_ignored = 0
  for row in csv_reader:
    if first_row:
      logger.info("Header is: " + repr(row))
      first_row = False
      continue  # skip header row

    if (row[indices['state_code']] == '' or
        row[indices['state_code']] == '99' or
        row[indices['state_code']] == '98'): # null, Embajadas, and Inhospitos
      logger.warning("Ignoring: " + repr(row))
      num_ignored += 1
      continue

    # Create center and table ids for the data in this row
    center_code = str.zfill(row[indices['center_code_new']], 9)
    table_code = center_code + "." + row[indices['table']]

    # aggregate votes by top-level (country), state, muni, parish, center, table
    add_votes(totals, row, indices)
    aggregate_votes(states, str.zfill(row[indices['state_code']], 2),
                    row, indices, 'state_name')
    aggregate_votes(munis, str.zfill(row[indices['muni_code']], 4), row, indices)
    aggregate_votes(parishes, str.zfill(row[indices['parish_code']], 6), row, indices)
    aggregate_votes(centers, center_code, row, indices, 'center_name')
    aggregate_votes(tables, table_code, row, indices,
                    name_func = lambda r, i: r[i['center_name']] + '-' + r[i['table']])

  print "Done aggregating. Ignored %d rows" % num_ignored
  return { 'country': {'00': totals},
           'state': states,
           'muni': munis,
           'parish': parishes,
           'center': centers,
           'table': tables }

def fill_participation(data, apr14=True):
  for level in data:
    for code in data[level]:
      if apr14:
        data[level][code]['particip'] = \
          utils.rounded_pct(data[level][code]['scrut_voters'],
                            data[level][code]['voters'])
      else: # 7o
        data[level][code]['particip'] = \
          utils.rounded_pct(data[level][code]['voting_voters'],
                      data[level][code]['scrut_voters'])

def fill_pcts(data):
  for level in data:
    for code in data[level]:
      data[level][code]['gov_pct'] = utils.rounded_pct(data[level][code]['gov'],
                                                       data[level][code]['valid'])
      data[level][code]['cap_pct'] = utils.rounded_pct(data[level][code]['cap'],
                                                       data[level][code]['valid'])

### Data filtering

# Copies 'voters' from all values in source to dest.
def fill_voters(source, dest):
  for place in source:
    for code in source[place]:
      if code in dest[place]:
        dest[place][code]['voters'] = source[place][code]['voters']

def filter_uncounted(votes):
  topop = list()
  for code in votes:
    if votes[code]['scrut_votes'] == 0:
      topop.append(code)
  for code in topop:
    votes.pop(code, None)
  print "Filtered %d places with 0 scrutinized votes" % len(topop)
  topop = list()
  for code in votes:
    if votes[code]['valid'] == 0:
      topop.append(code)
  for code in topop:
    votes.pop(code, None)
  print "Filtered %d more places with 0 valid votes" % len(topop)

# Finds the max number of voters at a place in the given voting set.
def max_voters(votes):
  max_voters = 0
  for code in votes:
    max_voters = max(max_voters, votes[code]['voters'])
  return max_voters

def compare_places(votes1, votes2):
  print "There were %d places in t1 and %d in t2" % (len(votes1), len(votes2))
  codes1 = set(votes1)
  codes2 = set(votes2)
  print "The following places existed in t1 but not t2: " + repr(codes1.difference(codes2))
  print "The following places existed in t2 but not t1: " + repr(codes2.difference(codes1))
  print "Max voters in t1 is %d and in t2 it is %d" % (max_voters(votes1), max_voters(votes2))


# Read in and clean data
data = [process_csv(csv_7o, indices_7o), process_csv(csv_14a, indices_14a)]
fill_participation(data[1])
fill_participation(data[0], False)
fill_pcts(data[0])
fill_pcts(data[1])
# for all places, voters in 2012 match those in 2013 (except maduro, which is negligible)
fill_voters(data[1], data[0])

print
print "There are %d states" % len(data[1]['state'])
print "There are %d munis" % len(data[1]['muni'])
print "There are %d parishes" % len(data[1]['parish'])
print "Comparing centers"
compare_places(data[0]['center'], data[1]['center'])
print "Comparing tables"
compare_places(data[0]['table'], data[1]['table'])

print
print "Filtering 7O"
filter_uncounted(data[0]['table'])
filter_uncounted(data[0]['center'])
print "Filtering 14A"
filter_uncounted(data[1]['table'])
filter_uncounted(data[1]['center'])

# CNE data weirdness in 7O:
print
odd_7o_table_codes = utils.filter_by(data[0]['table'], lambda v: v['voting_voters'] != v['scrut_votes'])
print "Tables in 7O where voting voters does not match scrutinized votes: %d" % len(odd_7o_table_codes)

# variables for easy access
tables = [data[0]['table'], data[1]['table']]
centers = [data[0]['center'], data[1]['center']]
parishes = [data[0]['parish'], data[1]['parish']]
munis = [data[0]['muni'], data[1]['muni']]
states = [data[0]['state'], data[1]['state']]

jt = {} # for joined_tables
good_codes = set(tables[0]).intersection(set(tables[1])).difference(odd_7o_table_codes)
for code in good_codes:
  jt[code] = [tables[0][code], tables[1][code]]

good_codes = set(centers[0]).intersection(set(centers[1]))
jc = {} # for joined_centers
for code in good_codes:
  jc[code] = [centers[0][code], centers[1][code]]

good_codes = set(parishes[0]).intersection(set(parishes[1]))
jp = {} # for joined_parishes
for code in good_codes:
  jp[code] = [parishes[0][code], parishes[1][code]]


