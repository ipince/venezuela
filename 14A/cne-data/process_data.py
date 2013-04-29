#!/usr/bin/python

import logging
import math
import matplotlib.pyplot as plt
import numpy as np
import csv
import utils
import import_data

from collections import defaultdict
# TODO(ipince): make this less nasty
from import_data import data, tables, centers, parishes, munis, states, jt, jc, odd_7o_table_codes


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

def short(votes):
  return '{ voters= ' + str(votes['voters']) + ',\tscrut_votes= ' + str(votes['scrut_votes']).zfill(2) + \
           ',\tvalid= ' + str(votes['valid']) + '\t gov= ' + str(votes['gov']) + \
           ' (' + str(votes['gov_pct']) + ')' + \
           ',\tcap= ' + str(votes['cap']).zfill(2) + ',\tparticip= ' + str(votes['particip']) + ' }'

print
maduro_dom_tables = utils.filter_by(data[1]['table'], lambda v: v['cap'] == 0)
chavez_dom_tables = utils.filter_by(data[0]['table'], lambda v: v['cap'] == 0)

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
utils.plot_wrap((gov_hist[1][1:], gov_hist[0]),
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

print "Gov got 0 votes in %d tables" % len(utils.filter_by(data[0]['table'], lambda v: v['gov'] == 0))


### Participation-related analysis

print "Histogram of participation diff"
diff = list()
for code in jt:
  diff.append(tables[1][code]['particip'] - tables[0][code]['particip'])
m = utils.mean(diff)
st = utils.stdev(diff)
print "Mean= %f , and stdev= %f " % (m, st)

#plt.hist(diff, bins=range(-30, 30))
#plt.show()

pbound = 98
geq = lambda v: v['particip'] >= pbound
print "Tables in 7O with >%d pct particip: %d" % (pbound, len(utils.filter_by(tables[0], geq)))
print "Tables in 14A with >%d pct particip: %d" % (pbound, len(utils.filter_by(tables[1], geq)))

#delta = round(m + 3*st, 2)
delta = 10
print "Tables in which there is more than %.2f pct participation difference:" % delta
codes = utils.compare_by(
  tables,
  lambda v1, v2: v2['particip'] - v1['particip'] > delta,
  output=False,
  exclude=odd_7o_table_codes)

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

# TODO: name/bday collision analysis

