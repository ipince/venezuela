#!/usr/bin/python

import logging
import matplotlib.pyplot as plt
import csv

from collections import defaultdict

logger = logging.getLogger('log')
logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler())

csv_14a = 'esdata_resultados_elecc_2013-04-14-v1_2.csv'
indices_14a = {
  'state_code': 0,
  'state_name': 1,
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
  'capriles': 12,
}

csv_7o = 'esdata_resultados_elecc_2012-10-07C.csv'
indices_7o = {
  'state_code': 0,
  'state_name': 1,
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
  'capriles': 12,
}

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
  totals['capriles'] += int(row[indices['capriles']])
  try:
    if 'voters' in indices: totals['voters'] += int(row[indices['voters']])
  except ValueError:
    logger.warning('Invalid number of voters in row: ' + repr(row))

def rounded_pct(num, den):
  if den == 0: return 'N/A'
  return int(round(100 * float(num) / float(den)))

def process_csv(filename, indices):
  csv_file = open(filename, 'rb')
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

    if (row[indices['state_code']] == '' or
        row[indices['state_code']] == '99' or
        row[indices['state_code']] == '98'): # null, Embajadas, and Inhospitos
      logger.warning("Ignoring: " + repr(row))
      num_ignored += 1
      continue

    # add to grand totals
    add_votes(totals, row, indices)

    # aggregate by state
    state_code = str.zfill(row[indices['state_code']], 2)
    if state_code not in states:
      states[state_code] = defaultdict(int)
      states[state_code]['name'] = row[indices['state_name']]
    add_votes(states[state_code], row, indices)

    # aggregate by center
    center_code = str.zfill(row[indices['center_code_new']], 9)
    if center_code not in centers:
      centers[center_code] = defaultdict(int)
      centers[center_code]['name'] = row[indices['center_name']]
    add_votes(centers[center_code], row, indices)
    itr += 1

    # aggregate by table
    table_code = center_code + "." + row[indices['table']]
    if table_code not in tables:
      tables[table_code] = defaultdict(int)
      tables[table_code]['name'] = row[indices['center_name']] + "-" + row[indices['table']]
    add_votes(tables[table_code], row, indices)

  print "Done aggregating. Ignored %d rows" % num_ignored
  return { 'country': {'00': totals}, 'state': states, 'center': centers, 'table': tables}

def fill_participation(data, apr14=True):
  for level in data:
    for code in data[level]:
      if apr14:
        data[level][code]['particip'] = \
          rounded_pct(data[level][code]['scrut_voters'],
                      data[level][code]['voters'])
      else: # 7o
        data[level][code]['particip'] = \
          rounded_pct(data[level][code]['voting_voters'],
                      data[level][code]['scrut_voters'])

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

def find_zero_participation(votes):
  print "Places with 0% participation:"
  count = 0
  for code in votes:
    if votes[code]['particip'] == 0:
      print code + ": " + repr(votes[code])
      count += 1
  print "There are %d places with 0 participation" % count

def plot_participation(votes):
  particip = list()
  for code in votes:
    particip.append(votes[code]['particip'])
  plt.hist(particip, bins=range(50, 100))
  plt.show()

def plot_participation_vs(votes, dim):
  part = list()
  xs = list()
  for code in votes:
    xs.append(votes[code][dim])
    part.append(votes[code]['particip'])
  plt.scatter(xs, part)
  plt.show()

data = [process_csv(csv_7o, indices_7o), process_csv(csv_14a, indices_14a)]
fill_participation(data[1])
fill_participation(data[0], False)

totals = data[1]['country']
states = data[1]['state']
centers = data[1]['center']
tables = data[0]['table']

filter_uncounted(tables)

#for state in states:
#  print state + ": " + repr(states[state])

print "num centers: " + str(len(data[0]['center']))

#print "Center with no scrutinized votes:"
#for code in centers:
#  if centers[code]['scrut_votes'] == 0:
#    print code + ": " + repr(centers[code])

def count_zeros(votes, dim):
  print "%s got 0 votes in the following tables:" % dim
  count = 0
  for code in votes:
    if votes[code][dim] == 0:
      print code + ": " + repr(votes[code])
      count += 1
  print "Total of %d tables" % count

count_zeros(tables, 'capriles')
count_zeros(tables, 'gov')

max_table = 0
for code in tables:
  max_table = max(max_table, tables[code]['voters'])
print "max table size: " + str(max_table)

#find_zero_participation(tables)


#plot_participation(data[1]['table'])
#plot_participation_vs(data[1]['table'], 'voters')
