#!/usr/bin/python

import utils

from import_data import tables, centers, parishes, munis, states

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

  tuple_rounded_pct = lambda (n, d): utils.rounded_pct(n, d)
  cumsum_gov_pct = map(tuple_rounded_pct, zip(cumsums['gov'], cumsums['valid']))
  cumsum_cap_pct = map(tuple_rounded_pct, zip(cumsums['cap'], cumsums['valid']))
  cumsum_null_pct = map(tuple_rounded_pct, zip(cumsums['null'], cumsums['valid']))

  utils.plot_wrap((cumsums['valid'], cumsum_gov_pct, 'r',
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

plot_all_pct_vs_cum_valid()
