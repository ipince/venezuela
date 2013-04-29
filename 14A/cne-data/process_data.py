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
      data[level][code]['cap_pct'] = rounded_pct(data[level][code]['cap'],
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

### Utility math-related functions

def rounded_pct(num, den):
  if den == 0: return 'N/A'
  return round(100 * float(num) / float(den), 2)

def mean(a):
  return float(sum(a)) / len(a)

def stdev(a):
  m = mean(a)
  return math.sqrt(sum((x-m) ** 2 for x in a) / len(a))

### Utility plotting functions

# Wraps plt.plot and optionally sets title, axis labels, and saves graph to disk
def plot_wrap(plotargs, title=None, xlabel=None, ylabel=None, filename=None):
  plt.ion()
  plt.figure()
  plt.plot(*plotargs)
  if title: plt.title(title)
  if xlabel: plt.xlabel(xlabel)
  if ylabel: plt.ylabel(ylabel)
  plt.grid()
  plt.draw()
  if filename: plt.savefig(filename)

### TODO(ipince): cleanup the functions below.

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
           ',\tcap= ' + str(votes['cap']).zfill(2) + ',\tparticip= ' + str(votes['particip']) + ' }'



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

print
print "Filtering 7O"
filter_uncounted(data[0]['table'])
filter_uncounted(data[0]['center'])
print "Filtering 14A"
filter_uncounted(data[1]['table'])
filter_uncounted(data[1]['center'])

# CNE data weirdness in 7O:
print
odd_7o_table_codes = filter_by(data[0]['table'], lambda v: v['voting_voters'] != v['scrut_votes'])
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
  jc[code] = [data[0]['center'][code], data[1]['center'][code]]

print
maduro_dom_tables = filter_by(data[1]['table'], lambda v: v['cap'] == 0)
chavez_dom_tables = filter_by(data[0]['table'], lambda v: v['cap'] == 0)

maduro_dom_chavez_not = maduro_dom_tables.difference(chavez_dom_tables)
print "Maduro dominated in %d tables that Chavez did not" % len(maduro_dom_chavez_not)
#for code in maduro_dom_chavez_not:
#  print data[0]['table'][code]

# graph gov diff
gov_nominal_diff = map(lambda vs: vs[1]['gov'] - vs[0]['gov'], jt.values())
gov_pct_diff = map(lambda vs: vs[1]['gov_pct'] - vs[0]['gov_pct'], jt.values())

print "max diff is %d " % max(gov_nominal_diff)
# TODO(ipince): change to use plt.hist() instead of plt.plot()
gov_hist = np.histogram(gov_nominal_diff,
                        bins=range(min(gov_nominal_diff), max(gov_nominal_diff)))
plot_wrap((gov_hist[1][1:], gov_hist[0]),
          title='Nominal pro-Chavez diff by table',
          xlabel='gov_votes_2013 - gov_votes_2012',
          ylabel='frequency',
          filename='gov_votes_diff_hist.png')

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
# TODO(ipince): do just 2013 election; no diffs
# joined! codes by size
codes_by_size = sorted(jt, key=lambda code: jt[code][1]['voters'])
plt.figure()
plt.scatter([jt[c][1]['voters'] for c in codes_by_size],
         [jt[c][1]['gov_pct'] - jt[c][0]['gov_pct'] for c in codes_by_size])
plt.title('Pro-Chavez % diff by table')
plt.xlabel('table size (registered voters)')
plt.ylabel('gov_pct_2013 - gov_pct_2012')
plt.grid()
plt.draw()
plt.savefig('gov_pct_diff_by_table_size.png')

codes_by_size = sorted(jc, key=lambda code: jc[code][1]['voters'])
plt.figure()
plt.scatter([jc[c][1]['voters'] for c in codes_by_size],
            [jc[c][1]['gov_pct'] - jc[c][0]['gov_pct'] for c in codes_by_size])
plt.title('Pro-Chavez % diff by center')
plt.xlabel('center size (registered voters)')
plt.ylabel('gov_pct_2013 - gov_pct_2012')
plt.grid()
plt.draw()
plt.savefig('gov_pct_diff_by_center_size.png')

print "Gov got 0 votes in %d tables" % len(filter_by(data[0]['table'], lambda v: v['gov'] == 0))

### Suggested analysis from Choquette.

# Notes from Choquette:
# TODO(ipince): vote % for each, vs turnout. also vs. total valid votes.
# per center, per table, per parish.

# TODO(ipince): find people that voted for cap in tables where he got 0 (or <5) votes. If you can find them (and believe them) => there was fraud.

# TODO(ipince): vote % vs. cumulative valid votes.
# TODO(ipince): do analysis of geographically random centers.

# Graph of candidate % over cumsum(valid-votes)

def cumsum(votes, dim, iter_codes):
  cumsum = list()
  for code in iter_codes:
    if not cumsum:
      cumsum.append(votes[code][dim])
    else:
      cumsum.append(cumsum[-1] + votes[code][dim])
  return cumsum

def cumsum_all(votes, iter_codes):
  cumsum_valid = cumsum(votes, 'valid', iter_codes)
  cumsum_gov = cumsum(votes, 'gov', iter_codes)
  cumsum_cap = cumsum(votes, 'cap', iter_codes)
  cumsum_null = cumsum(votes, 'null', iter_codes)
  return { 'valid': cumsum_valid, 'gov': cumsum_gov,
           'cap': cumsum_cap, 'null': cumsum_null }

def plot_pct_vs_cum_valid(votes, level, year):
  codes_by_valid = sorted(votes, key=lambda code: votes[code]['valid'])
  cumsums = cumsum_all(votes, codes_by_valid)

  tuple_rounded_pct = lambda (n, d): rounded_pct(n, d)
  cumsum_gov_pct = map(tuple_rounded_pct, zip(cumsums['gov'], cumsums['valid']))
  cumsum_cap_pct = map(tuple_rounded_pct, zip(cumsums['cap'], cumsums['valid']))
  cumsum_null_pct = map(tuple_rounded_pct, zip(cumsums['null'], cumsums['valid']))

  plot_wrap((cumsums['valid'], cumsum_gov_pct, 'r',
            cumsums['valid'], cumsum_cap_pct, 'b',
            cumsums['valid'], cumsum_null_pct, 'k'),
            title='Candidate %% vs cumulative valid votes, by %s' % level,
            xlabel='Cumulative valid votes (by %s)' % level,
            ylabel='Candidate % of votes',
            filename='candidate_pct_vs_cum_valid_by_%s_%d.png' % (level, year))

def plot_all_pct_vs_cum_valid():
  plot_pct_vs_cum_valid(tables[1], 'table', 2013)
  plot_pct_vs_cum_valid(centers[1], 'center', 2013)
  plot_pct_vs_cum_valid(parishes[1], 'parish', 2013)
  plot_pct_vs_cum_valid(munis[1], 'muni', 2013)
  plot_pct_vs_cum_valid(states[1], 'state', 2013)
  plot_pct_vs_cum_valid(tables[0], 'table', 2012)
  plot_pct_vs_cum_valid(centers[0], 'center', 2012)
  plot_pct_vs_cum_valid(parishes[0], 'parish', 2012)
  plot_pct_vs_cum_valid(munis[0], 'muni', 2012)
  plot_pct_vs_cum_valid(states[0], 'state', 2012)


### Participation-related analysis

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
#s = sorted([jt[c] for c in codes], key=lambda vs: vs[1]['gov_pct'], reverse=True)
s = sorted([jt[c] for c in codes], key=lambda vs: vs[1]['particip'] - vs[0]['particip'] , reverse=True)
#for elm in s:
#  print short(elm[0])
#  print short(elm[1])

print "gov rules on %d" % len(filter(lambda v: v['gov_pct'] >= 50, [tables[1][c] for c in codes]))
print "delta gov in those is %d" % (sum([tables[1][c]['gov'] for c in codes]) - sum([tables[0][c]['gov'] for c in codes]))
print "delta cap in those is %d" % (sum([tables[1][c]['cap'] for c in codes]) - sum([tables[0][c]['cap'] for c in codes]))

pairs = filter(lambda (k, v): v['particip'] > 98, tables[1].iteritems())

#find_zero_participation(tables)

#plot_participation(data[1]['table'])
#plot_participation_vs(data[1]['table'], 'voters')

# Null vote analysis


### Benford analysis

# ref: http://www.usfca.edu/fac-staff/huxleys/Benford.html
benford_1st = [30.1, 17.61, 12.49, 9.69, 7.92, 6.69, 5.8, 5.12, 4.58]
benford_2nd = [11.97, 11.39, 10.88, 10.43, 10.03, 9.67, 9.34, 9.04, 8.76, 8.50]

def dig_pct(votes, valid_digits, extract_digit):
  samples = filter(lambda d: d != -1, map(extract_digit, votes))
  dig_freq = defaultdict(int)
  for d in samples:
    dig_freq[d] += 1
  dig_pct = map(lambda d: 100 * float(dig_freq[d]) / len(samples), valid_digits)
  return dig_pct

def fst_dig_pct(votes, dim):
  return dig_pct(votes, range(1, 10),
                 lambda c: int(str(votes[c][dim])[0]) if votes[c][dim] != 0 else -1)

def snd_dig_pct(votes, dim):
  return dig_pct(votes, range(0, 10),
                 lambda c: int(str(votes[c][dim]).zfill(2)[1]) if votes[c][dim] > 9 else -1)

def plot_benford_1st(places, level):
  digs = range(1, 10)
  plot_wrap((digs, fst_dig_pct(places[1], 'cap'), 'bo-',
            digs, fst_dig_pct(places[0], 'cap'), 'b.-',
            digs, fst_dig_pct(places[1], 'gov'), 'ro-',
            digs, fst_dig_pct(places[0], 'gov'), 'r.-',
            digs, benford_1st, 'go-'),
            title='Benford\'s Law for the 1st digit, by %s' % level,
            xlabel='First digit',
            ylabel='Percentage of tallies (%)',
            filename='benford_1st_all_%s.png' % level)

def plot_benford_2nd(places, level):
  digs = range(0, 10)
  plot_wrap((digs, snd_dig_pct(places[1], 'cap'), 'bo-',
            digs, snd_dig_pct(places[0], 'cap'), 'b.-',
            digs, snd_dig_pct(places[1], 'gov'), 'ro-',
            digs, snd_dig_pct(places[0], 'gov'), 'r.-',
            digs, benford_2nd, 'go-'),
            title='Benford\'s Law for the 2nd digit, by %s' % level,
            xlabel='Second digit',
            ylabel='Percentage of tallies (%)',
            filename='benford_2nd_all_%s.png' % level)

def plot_all_benford():
  plot_benford_1st(states, 'state')
  plot_benford_1st(munis, 'muni')
  plot_benford_1st(parishes, 'parish')
  plot_benford_1st(centers, 'center')
  plot_benford_1st(tables, 'table')
  plot_benford_2nd(states, 'state')
  plot_benford_2nd(munis, 'muni')
  plot_benford_2nd(parishes, 'parish')
  plot_benford_2nd(centers, 'center')
  plot_benford_2nd(tables, 'table')


# TODO: name/bday collision analysis

