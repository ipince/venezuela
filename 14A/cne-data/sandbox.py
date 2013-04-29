#!/usr/bin/python

import matplotlib.pyplot as plt
import utils

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

