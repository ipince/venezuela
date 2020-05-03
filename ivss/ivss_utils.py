#!/usr/bin/python

import os

def read_batch(filepath):
  cedulas = [] # list of tuples with (nationality, id)
  with open(filepath, 'r') as f:
    lines = f.read().splitlines()
    for l in lines:
      if l.startswith('#'):
        continue
      parts = l.split()
      if len(parts) == 2:
        cedulas.append((parts[0], parts[1]))
      elif len(parts) == 1: # assume V
        cedulas.append(('V', int(l)))
      else:
        print "Invalid line in file: %s" % (l)
  return cedulas

def path(cedula, toplevel):
  # structure is cache/<2-digit-millions>/<3-digit-thousands>
  filled = str(cedula).zfill(9)
  millions_path = os.path.join(toplevel, filled[:3])
  thousands_path = os.path.join(millions_path, filled[3:6])
  if not os.path.exists(millions_path):
    os.makedirs(millions_path)
  if not os.path.exists(thousands_path):
    os.makedirs(thousands_path)
  return os.path.join(thousands_path, filled[6:] + '.html')
