#!/usr/bin/python

import utils

from collections import defaultdict
from import_data import tables, centers, parishes, munis, states

### Benford analysis

# ref: http://www.usfca.edu/fac-staff/huxleys/Benford.html
benford_1st = {
    1: 30.1, 2: 17.61, 3: 12.49,
    4: 9.69, 5: 7.92, 6: 6.69,
    7: 5.8, 8: 5.12, 9: 4.58 }
benford_2nd = {
    0: 11.97, 1: 11.39, 2: 10.88, 3: 10.43,
    4: 10.03, 5: 9.67, 6: 9.34, 7: 9.04, 8: 8.76, 9: 8.50 }

def dig_freq(votes, extract_digit):
  samples = filter(lambda d: d != -1, map(extract_digit, votes))
  dig_freq = defaultdict(int)
  for d in samples:
    dig_freq[d] += 1
  return dig_freq

def dig_pct(freq, valid_digits):
  # valid_digits needed because some counts are 0
  total = sum(freq.values())
  dig_pct = map(lambda d: 100 * float(freq[d]) / total, valid_digits)
  return dig_pct

def fst_dig_freq(votes, dim):
  return dig_freq(votes, 
                  lambda c: int(str(votes[c][dim])[0]) if votes[c][dim] != 0 else -1)

def snd_dig_freq(votes, dim):
  return dig_freq(
      votes,
      lambda c: int(str(votes[c][dim]).zfill(2)[1]) if votes[c][dim] > 9 else -1)

def fst_dig_pct(freq):
  return dig_pct(freq, range(1, 10))

def snd_dig_pct(freq):
  return dig_pct(freq, range(0, 10))

def calc_chi(samples, expected):
  chi = 0
  print 'samples: ' + repr(samples)
  print 'expected: ' + repr(expected)
  for i in samples:
    term = pow(samples[i] - expected[i], 2) / expected[i]
    print 'sample is %d, expected %d; adding %d' % (samples[i], expected[i], term)
    chi += term
  return chi

def get_expected(weights, total):
  return dict([(k, v * total / 100) for (k, v) in weights.items()])

def plot_benford_1st(places, level):
  digs = range(1, 10)

  cap2013 = fst_dig_freq(places[1], 'cap')
  cap2012 = fst_dig_freq(places[0], 'cap')
  gov2013 = fst_dig_freq(places[1], 'gov')
  gov2012 = fst_dig_freq(places[0], 'gov')

  print 'Pearson X^2 statistics for first digit:'
  print 'cap 2013 at %s: %.2f' % (level, calc_chi(cap2013, get_expected(benford_1st, sum(cap2013.values()))))
  print 'cap 2012 at %s: %.2f' % (level, calc_chi(cap2012, get_expected(benford_1st, sum(cap2012.values()))))
  print 'gov 2013 at %s: %.2f' % (level, calc_chi(gov2013, get_expected(benford_1st, sum(gov2013.values()))))
  print 'gov 2012 at %s: %.2f' % (level, calc_chi(gov2012, get_expected(benford_1st, sum(gov2012.values()))))

  utils.plot_wrap((digs, fst_dig_pct(cap2013), 'bo-',
    digs, fst_dig_pct(cap2012), 'b.--',
    digs, fst_dig_pct(gov2013), 'ro-',
    digs, fst_dig_pct(gov2012), 'r.--',
    digs, benford_1st.values(), 'go-'),
    title='Benford\'s Law for the 1st digit, by %s' % level,
    xlabel='First digit',
    ylabel='Percentage of vote counts with corresponding 1st digit (%)',
    labels=['Capriles 2013', 'Capriles 2012', 'Maduro 2013', 'Chavez 2012', 'Benford'],
    filename='benford_1st_all_%s.png' % level)

def plot_benford_2nd(places, level):
  digs = range(0, 10)

  cap2013 = snd_dig_freq(places[1], 'cap')
  cap2012 = snd_dig_freq(places[0], 'cap')
  gov2013 = snd_dig_freq(places[1], 'gov')
  gov2012 = snd_dig_freq(places[0], 'gov')
  print 'Pearson X^2 statistics for second digit:'
  print 'cap 2013 at %s: %.2f' % (level, calc_chi(cap2013, [sum(cap2013.values()) * b/100 for b in benford_2nd]))
  print 'cap 2012 at %s: %.2f' % (level, calc_chi(cap2012, [sum(cap2012.values()) * b/100 for b in benford_2nd]))
  print 'gov 2013 at %s: %.2f' % (level, calc_chi(gov2013, [sum(gov2013.values()) * b/100 for b in benford_2nd]))
  print 'gov 2012 at %s: %.2f' % (level, calc_chi(gov2012, [sum(gov2012.values()) * b/100 for b in benford_2nd]))

  utils.plot_wrap((digs, snd_dig_pct(cap2013), 'bo-',
    digs, snd_dig_pct(cap2012), 'b.--',
    digs, snd_dig_pct(gov2013), 'ro-',
    digs, snd_dig_pct(gov2012), 'r.--',
    digs, benford_2nd, 'go-'),
    title='Benford\'s Law for the 2nd digit, by %s' % level,
    xlabel='Second digit',
    ylabel='Percentage of vote counts with corresponding 2nd digit (%)',
    labels=['Capriles 2013', 'Capriles 2012', 'Maduro 2013', 'Chavez 2012', 'Benford'],
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

plot_all_benford()

print "min for cap2013 is %d" % min([tables[1][code]['cap'] for code in tables[1]])
print "max for cap2013 is %d" % max([tables[1][code]['cap'] for code in tables[1]])
print "min for gov2013 is %d" % min([tables[1][code]['gov'] for code in tables[1]])
print "max for gov2013 is %d" % max([tables[1][code]['gov'] for code in tables[1]])
print "min for voters is %d" % min([tables[1][code]['voters'] for code in tables[1]])
print "max for voters is %d" % max([tables[1][code]['voters'] for code in tables[1]])

utils.hist_wrap(([tables[1][code]['voters'] for code in tables[1]], 200), filename='table-voters.png')
utils.hist_wrap(([tables[1][code]['cap'] for code in tables[1]], 200), filename='table-cap.png')
utils.hist_wrap(([tables[1][code]['gov'] for code in tables[1]], 200), filename='table-gov.png')
utils.hist_wrap(([centers[1][code]['voters'] for code in centers[1]], 200), filename='center-voters.png')
import matplotlib.pyplot as plt
plt.figure()
plt.hist([centers[1][code]['voters'] for code in centers[1]], 200, cumulative=True)
plt.show()
plt.savefig('center-cum_hist.png')
plt.figure()
plt.hist([tables[1][code]['voters'] for code in tables[1]], 200, cumulative=True)
plt.show()
plt.savefig('table-cum_hist.png')

utils.hist_wrap(([centers[1][code]['cap'] for code in centers[1]], 200), filename='center-cap.png')
utils.hist_wrap(([centers[1][code]['gov'] for code in centers[1]], 200), filename='center-gov.png')
