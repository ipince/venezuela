#!/usr/bin/python

import logging
import math
import matplotlib.pyplot as plt
import numpy as np
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
  return round(100 * float(num) / float(den), 2)

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
      logger.info("Header is: " + repr(row))
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

def fill_pcts(data):
  for level in data:
    for code in data[level]:
      data[level][code]['gov_pct'] = rounded_pct(data[level][code]['gov'],
                                                 data[level][code]['valid'])
      data[level][code]['cap_pct'] = rounded_pct(data[level][code]['capriles'],
                                                 data[level][code]['valid'])

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

def find_zero_participation(votes):
  print "Places with 0% participation:"
  count = 0
  for code in votes:
    if votes[code]['particip'] == 0:
      print code + ": " + repr(votes[code])
      count += 1
  print "There are %d places with 0 participation" % count

def plot_hist(votes, dim):
  points = list()
  for code in votes:
    points.append(votes[code]['dim'])
  plt.hist(points)
  plt.show()

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

def compare_places(votes1, votes2):
  print "There were %d places in t1 and %d in t2" % (len(votes1), len(votes2))
  codes1 = set(votes1)
  codes2 = set(votes2)
  print "The following places existed in t1 but not t2: " + repr(codes1.difference(codes2))
  print "The following places existed in t2 but not t1: " + repr(codes2.difference(codes1))
  print "Max voters in t1 is %d and in t2 it is %d" % (max_voters(votes1), max_voters(votes2))

# Finds the max number of voters at a place in the given voting set.
def max_voters(votes):
  max_voters = 0
  for code in votes:
    max_voters = max(max_voters, votes[code]['voters'])
  return max_voters

def filter_by(votes, pred, exclude=set(), output=False):
  codes = set()
  for code in votes:
    if votes[code]['scrut_votes'] == 0:
      logger.warning("Skipping set for having 0 scrut votes: " + repr(votes[code]))
      continue
    if pred(votes[code]):
      if output: print code + ": " + repr(votes[code])
      codes.add(code)
  return codes

# Takes in array (of size 2) of voting sets, applies pred to both of them.
def compare_by(votes_arr, pred, exclude=set(), output=False):
  codes = set(votes_arr[0]).intersection(set(votes_arr[1]))
  codes = codes.difference(exclude)
  matching = set()
  for code in codes:
    if pred(votes_arr[0][code], votes_arr[1][code]):
      if output:
        print code + ": " + repr(votes_arr[0][code])
        print code + ": " + repr(votes_arr[1][code])
      matching.add(code)
  return matching

def short(votes):
  return '{ voters= ' + str(votes['voters']) + ',\tscrut_votes= ' + str(votes['scrut_votes']).zfill(2) + \
           ',\tvalid= ' + str(votes['valid']) + '\t gov= ' + str(votes['gov']) + \
           ' (' + str(votes['gov_pct']) + ')' + \
           ',\tcap= ' + str(votes['capriles']).zfill(2) + ',\tparticip= ' + str(votes['particip']) + ' }'

# Read in and clean data
data = [process_csv(csv_7o, indices_7o), process_csv(csv_14a, indices_14a)]
fill_participation(data[1])
fill_participation(data[0], False)
fill_pcts(data[0])
fill_pcts(data[1])
# for all places, voters in 2012 match those in 2013 (except maduro, which is negligible)
fill_voters(data[1], data[0])

print
print "Comparing centers"
compare_places(data[0]['center'], data[1]['center'])
print "Comparing tables"
compare_places(data[0]['table'], data[1]['table'])

# varibles for easy access
tables = [data[0]['table'], data[1]['table']]

print
print "Filtering 7O"
filter_uncounted(data[0]['table'])
print "Filtering 14A"
filter_uncounted(data[1]['table'])

# CNE data weirdness in 7O:
print
odd_7o_table_codes = filter_by(data[0]['table'], lambda v: v['voting_voters'] != v['scrut_votes'])
print "Tables in 7O where voting voters does not match scrutinized votes: %d" % len(odd_7o_table_codes)

joined_tables = {}
good_codes = set(tables[0]).intersection(set(tables[1])).difference(odd_7o_table_codes)
for code in good_codes:
  joined_tables[code] = [tables[0][code], tables[1][code]]

print
maduro_dom_tables = filter_by(data[1]['table'], lambda v: v['capriles'] == 0)
chavez_dom_tables = filter_by(data[0]['table'], lambda v: v['capriles'] == 0)

maduro_dom_chavez_not = maduro_dom_tables.difference(chavez_dom_tables)
print "Maduro dominated in %d tables that Chavez did not" % len(maduro_dom_chavez_not)
#for code in maduro_dom_chavez_not:
#  print data[0]['table'][code]

# graph gov diff
gov_nominal_diff = map(lambda vs: vs[1]['gov'] - vs[0]['gov'], joined_tables.values())
gov_pct_diff = map(lambda vs: vs[1]['gov_pct'] - vs[0]['gov_pct'], joined_tables.values())

print "max diff is %d " % max(gov_nominal_diff)
# TODO(ipince): change to use plt.hist() instead of plt.plot()
gov_hist = np.histogram(gov_nominal_diff,
                        bins=range(min(gov_nominal_diff), max(gov_nominal_diff)))
plt.ion()
plt.plot(gov_hist[1][1:], gov_hist[0])
plt.title('Nominal pro-Chavez diff by table')
plt.xlabel('gov_votes_2013 - gov_votes_2012')
plt.ylabel('frequency')
plt.grid()
plt.draw()
plt.savefig('gov_votes_diff_hist.png')

plt.ylim(0, 20)
plt.draw()
plt.savefig('gov_votes_diff_hist_zoom.png')

plt.figure()
plt.plot(gov_hist[1][1:], np.cumsum(gov_hist[0]))
plt.title('Cumulative nominal pro-Chavez diff by table')
plt.xlabel('gov_votes_2013 - gov_votes_2012')
plt.ylabel('cum sum of frequencies')
plt.grid()
plt.draw()
plt.savefig('gov_votes_diff_cumsum.png')

plt.figure()
plt.hist(gov_pct_diff, bins=200)
plt.title('Pro-Chavez % diff by table')
plt.xlabel('gov_pct_2013 - gov_pct_2012')
plt.ylabel('frequency')
plt.grid()
plt.draw()
plt.savefig('gov_pct_diff.png')

plt.ylim(0, 20)
plt.draw()
plt.savefig('gov_pct_diff_zoom.png')

plt.figure()
plt.hist(gov_pct_diff, bins=100, cumulative=True, histtype='step')
plt.title('Cumulative pro-Chavez % diff by table')
plt.xlabel('gov_pct_2013 - gov_pct_2012')
plt.ylabel('cum sum of frequencies')
plt.grid()
plt.draw()
plt.savefig('gov_pct_diff_cumsum.png')

# TODO(ipince): do by valid too
# TODO(ipince): do by center
# TODO(ipince): do with added weird centers
jt = joined_tables
codes_by_size = sorted(joined_tables, key=lambda code: joined_tables[code][1]['voters'])
plt.figure()
plt.scatter([jt[c][1]['voters'] for c in codes_by_size],
         [jt[c][1]['gov_pct'] - jt[c][0]['gov_pct'] for c in codes_by_size])
plt.title('Pro-Chavez % diff by table')
plt.xlabel('table size')
plt.ylabel('gov_pct_2013 - gov_pct_2012')
plt.grid()
plt.draw()
plt.savefig('gov_pct_diff_by_table_size.png')


print "Gov got 0 votes in %d tables" % len(filter_by(data[0]['table'], lambda v: v['gov'] == 0))

### Participation-related analysis

def mean(a):
  return float(sum(a)) / len(a)

def stdev(a):
  m = mean(a)
  return math.sqrt(sum((x-m) ** 2 for x in a) / len(a))

print "Histogram of participation diff"
diff = list()
good_codes = set(tables[0]).intersection(set(tables[1])).difference(odd_7o_table_codes)
for code in good_codes:
  diff.append(tables[1][code]['particip'] - tables[0][code]['particip'])
m = mean(diff)
st = stdev(diff)
print "Mean= %f , and stdev= %f " % (m, st)

#plt.hist(diff, bins=range(-30, 30))
#plt.show()

pbound = 98
geq = lambda v: v['particip'] >= pbound
print "Tables in 7O with >%d pct particip: %d" % (pbound, len(filter_by(tables[0], geq)))
print "Tables in 14A with >%d pct particip: %d" % (pbound, len(filter_by(tables[1], geq)))

#delta = round(m + 3*st, 2)
delta = 10
print "Tables in which there is more than %.2f pct participation difference:" % delta
codes = compare_by(tables, lambda v1, v2: v2['particip'] - v1['particip'] > delta, output=False, exclude=odd_7o_table_codes)

print "There are %d such tables" % len(codes)
#s = sorted([joined_tables[c] for c in codes], key=lambda vs: vs[1]['gov_pct'], reverse=True)
s = sorted([joined_tables[c] for c in codes], key=lambda vs: vs[1]['particip'] - vs[0]['particip'] , reverse=True)
#for elm in s:
#  print short(elm[0])
#  print short(elm[1])

print "gov rules on %d" % len(filter(lambda v: v['gov_pct'] >= 50, [tables[1][c] for c in codes]))
print "delta gov in those is %d" % (sum([tables[1][c]['gov'] for c in codes]) - sum([tables[0][c]['gov'] for c in codes]))
print "delta cap in those is %d" % (sum([tables[1][c]['capriles'] for c in codes]) - sum([tables[0][c]['capriles'] for c in codes]))

pairs = filter(lambda (k, v): v['particip'] > 98, tables[1].iteritems())

#find_zero_participation(tables)

#plot_participation(data[1]['table'])
#plot_participation_vs(data[1]['table'], 'voters')

# Null vote analysis


# Benford analysis


# TODO: name/bday collision analysis

