#!/usr/bin/python

import math
import matplotlib.pyplot as plt

### Utility math-related functions

def rounded_pct(num, den):
  if den == 0: return 'N/A'
  return round(100 * float(num) / float(den), 2)

def mean(a):
  return float(sum(a)) / len(a)

def stdev(a):
  m = mean(a)
  return math.sqrt(sum((x-m) ** 2 for x in a) / len(a))

### Comparing sets of voting data

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

# TODO(ipince): change api to not be so nasty.
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


### Utility plotting functions

# Wraps plt.plot and optionally sets title, axis labels, and saves graph to disk
def plot_wrap(plotargs, title=None, xlabel=None, ylabel=None, labels=None, filename=None):
  plt.ion()
  plt.figure()
  p = plt.plot(*plotargs)
  if title: plt.title(title)
  if xlabel: plt.xlabel(xlabel)
  if ylabel: plt.ylabel(ylabel)
  plt.grid()
  if labels: plt.legend(p, labels)
  plt.draw()
  if filename: plt.savefig(filename)

def hist_wrap(histargs, title=None, xlabel=None, ylabel=None, filename=None):
  plt.ion()
  plt.figure()
  plt.hist(*histargs)
  if title: plt.title(title)
  if xlabel: plt.xlabel(xlabel)
  if ylabel: plt.ylabel(ylabel)
  plt.grid()
  plt.draw()
  if filename: plt.savefig(filename)

def scatter_wrap(scatargs, title=None, xlabel=None, ylabel=None, filename=None):
  plt.ion()
  plt.figure()
  plt.scatter(*scatargs)
  if title: plt.title(title)
  if xlabel: plt.xlabel(xlabel)
  if ylabel: plt.ylabel(ylabel)
  plt.grid()
  plt.draw()
  if filename: plt.savefig(filename)


### Printing

def short(votes):
  return '{ voters= ' + str(votes['voters']) + ',\tscrut_votes= ' + str(votes['scrut_votes']).zfill(2) + \
           ',\tvalid= ' + str(votes['valid']) + '\t gov= ' + str(votes['gov']) + \
           ' (' + str(votes['gov_pct']) + ')' + \
           ',\tcap= ' + str(votes['cap']).zfill(2) + ',\tparticip= ' + str(votes['particip']) + ' }'


