#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np
import utils

# TODO(ipince): make this less nasty
from import_data import data, tables, centers, parishes, munis, states, jt, jc, jp

print
cutoff = 95

cha_dom_tables = utils.filter_by(tables[0], lambda v: v['gov_pct'] >= cutoff)
mad_dom_tables = utils.filter_by(tables[1], lambda v: v['gov_pct'] >= cutoff)
cap_dom_tables = utils.filter_by(tables[1], lambda v: v['cap_pct'] >= cutoff)

mad_dom_cha = mad_dom_tables.difference(cha_dom_tables)

print 'Using a cutoff of %d%%' % cutoff
print 'Capriles dominated in %d tables.' % len(cap_dom_tables)
print 'Maduro dominated in %d tables. Chavez in %d' % (len(mad_dom_tables), len(cha_dom_tables))

print 'Maduro dominated in %d tables that Chavez did not' % len(mad_dom_cha)
for code in mad_dom_cha:
  print utils.short(tables[0][code])
  print utils.short(tables[1][code])

# Do any of those have significant support for Capriles that was gone in 2013?


# Compare Maduro vs Chavez at table level.
# TODO(ipince): do the same at center level, parish?

def plot_hist(data, dim, level):
  # TODO(ipince): which bins to use?
  #utils.hist_wrap((data, range(int(min(data)), int(max(data)))),
  utils.hist_wrap((data, 200),
    title='%s diff by %s' % (dim, level),
    xlabel='%s_2013 - %s_2012' % (dim, dim),
    ylabel='frequency',
    filename='%s_diff_hist_by_%s.png' % (dim, level))
  # save a zoomed-in copy
  plt.ylim(0, 20)
  plt.draw()
  plt.savefig('%s_diff_hist_by_%s_zoom.png' % (dim, level))

def plot_cumulative_hist(data, dim, level):
  h = np.histogram(data, bins=range(int(min(data)), int(max(data))))
  utils.plot_wrap((h[1][1:], np.cumsum(h[0])),
    title='%s cumulative diff by %s' % (dim, level),
    xlabel='%s_2013 - %s_2012' % (dim, dim),
    ylabel='cumulative sum of frequencies',
    filename='%s_diff_cumsum_hist_by_%s.png' % (dim, level))

def plot_diff_hists(joined, dim, level):
  diffs = map(lambda vs: vs[1][dim] - vs[0][dim], joined.values())
  plot_hist(diffs, dim, level)
  plot_cumulative_hist(diffs, dim, level)

def plot_all_diff_hists():
  plot_diff_hists(jt, 'gov', 'table')
  plot_diff_hists(jt, 'cap', 'table')
  plot_diff_hists(jt, 'gov_pct', 'table')
  plot_diff_hists(jt, 'cap_pct', 'table')
  plot_diff_hists(jc, 'gov', 'center')
  plot_diff_hists(jc, 'cap', 'center')
  plot_diff_hists(jc, 'gov_pct', 'center')
  plot_diff_hists(jc, 'cap_pct', 'center')

plot_all_diff_hists()

# Scatter plots of diffs by level (table, center) size (voters, valid)
# TODO(ipince): do with added weird centers
# TODO(ipince): do just 2013 election; no diffs
# joined! codes by size

def plot_diff_scatter(joined, dim, size_dim, level):
  # take size wrt to 2013
  codes_by_size = sorted(joined, key=lambda code: joined[code][1][size_dim])
  utils.scatter_wrap(
    ([joined[c][1][size_dim] for c in codes_by_size],
     [joined[c][1][dim] - joined[c][0][dim] for c in codes_by_size],
     20, 'r' if 'gov' in dim else 'b', 'o'),
    title='%s diff by %s' % (dim, level),
    xlabel='%s size (wrt number of %s)' % (level, size_dim),
    ylabel='%s_2013 - %s_2012' % (dim, dim),
    filename='%s_diff_vs_%s_size_wrt_%s.png' % (dim, level, size_dim))

def plot_all_diff_scatters():
  plot_diff_scatter(jt, 'gov_pct', 'voters', 'table')
  plot_diff_scatter(jc, 'gov_pct', 'voters', 'center')
  plot_diff_scatter(jp, 'gov_pct', 'voters', 'parish')

  plot_diff_scatter(jt, 'cap_pct', 'voters', 'table')
  plot_diff_scatter(jc, 'cap_pct', 'voters', 'center')
  plot_diff_scatter(jp, 'cap_pct', 'voters', 'parish')

plot_all_diff_scatters()

