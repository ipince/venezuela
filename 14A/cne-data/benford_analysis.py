#!/usr/bin/python

import utils

from collections import defaultdict
from import_data import tables, centers, parishes, munis, states

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
  utils.plot_wrap((digs, fst_dig_pct(places[1], 'cap'), 'bo-',
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
  utils.plot_wrap((digs, snd_dig_pct(places[1], 'cap'), 'bo-',
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

plot_all_benford()
