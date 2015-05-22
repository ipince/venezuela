#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import codecs
import os
import urllib2
import itertools
import time
import re
from collections import defaultdict
from lxml import etree


def cached_url(url):
  return os.path.join("htmlcache", url.replace("/", "_").replace(":", "_"))

def parse2(url):
  cached = cached_url(url)
  contents = ""
  if os.path.exists(cached):
    #print "Reading from cached file %s" % cached
    contents = file(cached).read()
  else:
    #print "Fetching: " + url
    contents = urllib2.urlopen(url).read()
    outfile = file(cached, 'w')
    outfile.write(contents)
  return etree.HTML(contents)

def parse(link):
  """Returns an etree-parsed tree from the given link. Only looks Locally.
  """
  contents = file(link).read()
  return etree.HTML(contents)

def extract_nav_links(tree, xpath='//li[@class="region-nav-item"]/a', ignore=[]):
  """Returns a map { <link-name>: <link> } from extracting the navigation links.
  """
  links = {}
  for elem in tree.xpath(xpath):
    # gives you UTF-8 encoded obj of type 'str'
    txt = codecs.encode(elem.text, 'utf-8')
    if (txt not in ignore):
      # links are relative, so preprend path
      newlink = url_path + elem.get('href')
      parts = newlink.split('/')
      while '..' in parts:
        i = parts.index('..')
        parts.pop(i - 1)
        parts.pop(i - 1)
      links[txt] = '/'.join(parts)
  #print "\tExtracted links: " + str(links)
  return links

def extract_data(place, tree):
  """Returns a list of tuples. Each tuple contains the muni_index, candidate_votes dict, and a total_votes dict.
  """
  extracted_data = []
  try:
    update_time = extract_update_time(tree)
  except ValueError:
    print place
  containers = tree.xpath('//div[starts-with(@id, "resultDiv")]')
  for container in containers:
    muni_index = int(container.get('id')[len('resultDiv.'):])
    headline = tree.xpath('//a[@href="javascript:Show(\'resultDiv.' + str(muni_index) + '\');"]')[0].text
    if 'alcalde' not in headline.lower():
      # ignore non-mayor results
      continue
    candidate_votes = extract_candidate_votes(container)
    total_votes = extract_total_votes(container)
    extracted_data.append((muni_index, update_time, candidate_votes, total_votes))
  if len(extracted_data) == 0:
    extracted_data.append((None, update_time, None, None))
  return extracted_data

def print_tree(tree):
  """Prints an etree tree.
  """
  print(etree.tostring(tree, pretty_print=True))

def extract_candidate_votes(tree):
  """Extracts the candidate votes from a subtree that starts at the resultDiv level.
  """
  candidate_votes = {}
  candidates = []
  votes = []
  for e in tree.xpath('div[@id="tablaResultados"]//tr[@class="tbsubtotalrow"]//a'):
    candidates.append(codecs.encode(e.text, 'utf-8'))
  for e in tree.xpath('div[@id="tablaResultados"]//tr[@class="tbsubtotalrow"]/td/span'):
    if '%' in e.text:
      continue  # ignore percentages
    votes.append(int(e.text.replace('.', '')))
  for (i, candidate) in enumerate(candidates):
    candidate_votes[candidate] = votes[i];
  return candidate_votes

#  for tr in tree.xpath('//tr[@class="tbsubtotalrow"]'):
#    cells = tr.xpath('td[@class="lightRowContent"]/span')
#    votes[codecs.encode(cells[0][0].text, 'utf-8')] = str(cells[1].text).replace('.', '')
#  #print "\tExtracted candidate votes: " + str(votes)
#  return votes

def extract_total_votes(tree):
  """ Extracts the summary on "ficha tecnica" into a map
  """
  totals = {}
  for row in tree.xpath('div[@id="fichaTecnica"]//tr[@class="tblightrow"]'):
    keys = row.xpath('td/span/b')
    values = row.xpath('td[last()]')
    for i in range(len(keys)):
      if (values[i].text):
        totals[codecs.encode(keys[i].text, 'utf-8')] = str(values[i].text).replace('.', '')
  #print "\tExtracted totals: " + str(totals)
  return totals

def extract_update_time(tree):
  txt = []
  for e in tree.xpath('//tr[@class="tblightrow"]/td[@width="100%"]'):
    txt.append(e.text)
  txt = ' '.join(txt)
  txt = txt.replace('diciembre', 'dec')
  update_time = time.strftime('%x %X', time.strptime(txt, '%d %b %Y %H:%M')) + ' -0430'
  return update_time

'''
def write_to_file(votes):
  state_based = ''
  muni_based = ''
  parish_based = ''
  center_based = ''
  state_centers = {}
  sep = ','
  region_headers = ["Estado", "Municipio", "Parroquia", "Centro"]
  # hack: reoder the elements in the headers (I know the order, so this is kind of arbitrary):
  reorder = [10, 0, 13, 3, 5, 2, 9, 1, 6, 11, 8, 7, 12, 4]
  voting_headers = [votes.items()[0][1]["total"].keys()[r] for r in reorder]
  for state in sorted(votes.keys()):
    if state_based == '': state_based += sep.join(region_headers[:1] + voting_headers) + "\n"
    state_based += sep.join([state] + [votes[state]["total"][v] for v in voting_headers]) + "\n"
    centers_for_state = ''
    for muni in votes[state]:
      if muni == "total":
        continue
      if muni_based == '':
        muni_based += sep.join(region_headers[:2] + voting_headers) + "\n"
      muni_based += sep.join([state, muni] + [votes[state][muni]["total"][v] for v in voting_headers]) + "\n"
      for parish in votes[state][muni]:
        if parish == "total":
          continue
        if parish_based == '':
          parish_based += sep.join(region_headers[:3] + voting_headers) + "\n"
        parish_based += sep.join([state, muni, parish] + [votes[state][muni][parish]["total"][v] for v in voting_headers]) + "\n"
        for center in votes[state][muni][parish]:
          if center == "total":
            continue
          if center_based == '':
            center_based += sep.join(region_headers[:4] + voting_headers) + "\n"
          center_based += sep.join([state, muni, parish, center] + [votes[state][muni][parish][center][v] for v in voting_headers]) + "\n"
          if centers_for_state == '':
            centers_for_state = sep.join(region_headers[:4] + voting_headers) + "\n"
          centers_for_state += sep.join([state, muni, parish, center] + [votes[state][muni][parish][center][v] for v in voting_headers]) + "\n"
    # state is done here.
    state_centers[state.lower().replace("edo.", "").replace(".", "-").replace(" ", "")] = centers_for_state

  file(os.path.join('data', 'state-all.csv'), 'w').write(state_based)
  file(os.path.join('data', 'muni-all.csv'), 'w').write(muni_based)
  file(os.path.join('data', 'parish-all.csv'), 'w').write(parish_based)
  file(os.path.join('data', 'center-all.csv'), 'w').write(center_based)
  for state in state_centers:
    file(os.path.join('data', 'centers-' + state + '.csv'), 'w').write(state_centers[state])
'''

HEADER = ['codigo', 'fecha_actualizado', 'municipio_id', 'estado', 'municipio', 'parroquia', 'centro', 'mesa',
          'candidato', 'candidato_partidos', 'votos', 'votos_partido',
          'electores_esperados', 'electores_actas_transmitidas', 'electores_escrutados',
          'votos_escrutados', 'votos_validos', 'votos_nulos', 'actas_totales', 'actas_escrutadas',
          'url', 'fecha_scrape']
ORDERED_SUMMARY_HEADERS = ['ELECTORES ESPERADOS', 'ELECTORES EN ACTAS TRANSMITIDAS', 'ELECTORES ESCRUTADOS',
    'VOTOS ESCRUTADOS', 'VOTOS VÁLIDOS', 'VOTOS NULOS', 'ACTAS TOTALES', 'ACTAS ESCRUTADAS']
DONE_CODES = set()

def create_output_lines(link, muni_id, update_time, place, candidate_votes, total_votes, scrape_time):
  lines = []
  code = re.search(r'reg_(\d+)\.html$', link).group(1)
  if code in DONE_CODES:
    print 'WARNING: trying to create output for results we\'ve already processed'
    return lines
  baseline = [code, update_time, muni_id, place[0], place[1], place[2], place[3], place[4]]
  if not muni_id:
    # Page that has no results: write empty line and return
    line = list(baseline)
    line += [None] * 12  # candidate + total_votes parts
    line += [link, scrape_time]
    lines.append(line)
    DONE_CODES.add(code)
    return lines
  for candidate in candidate_votes:
    line = list(baseline)
    line += [candidate, None, candidate_votes[candidate], None]
    line += [None] * 8  # total_votes part
    line += [link, scrape_time]
    lines.append(line)
  line = list(baseline)
  line += [None] * 4  # candidate part
  line += [total_votes[i] for i in ORDERED_SUMMARY_HEADERS]
  line += [link, scrape_time]
  lines.append(line)
  DONE_CODES.add(code)
  return lines

url_root = 'www.cne.gob.ve/resultado_municipal_2013/';
url_path = url_root + 'r/1/'
country_url = url_path + 'reg_000000.html'

# STEP 1: Put all the links that we care about in a set.
to_visit = set()
visited = set()

to_visit.add(((None, None, None, None, None), country_url))

t0 = time.time()
visited_since = 0
interval = 1000

csvfile = open('out.csv', 'wb')
writer = csv.writer(csvfile)
writer.writerow(HEADER)

while to_visit:
  (place, link) = to_visit.pop()
  visited.add(place)

  # Timing and logging
  visited_since += 1
  if visited_since == interval:
    elapsed = time.time() - t0
    print 'Visited %d links in %d seconds' % (interval, elapsed)
    visited_since = 0
    t0 = time.time()

  tree = parse(link)

  # Add links this page points to, if any (all should have links, except table-level pages)
  links = extract_nav_links(tree)
  if links and (not place[0] or 'metropolitano' not in place[0].lower()):
    current_level = [idx for idx, val in enumerate(place) if not val][0]
    for name, link in links.iteritems():
      new_place = place[:current_level] + (name,) + place[current_level+1:]
      if new_place not in visited:
        to_visit.add((new_place, link))

  # If the page is Muni-level or lower, or if it's a District, then extract voting data
  if place[1] or (place[0] and 'metropolitano' in place[0].lower()):
    data = extract_data(place, tree)
    scrape_time = time.strftime('%x %X %z', time.localtime(os.path.getctime(link)))
    if len(data) > 1:
      # More than one set of results means we're at an "overloaded" state; we want all
      print 'Found %d results in page %s-%s-%s-%s-%s ' % ((len(data),) + place)
    lines = []
    for d in data:
      lines.extend(create_output_lines(link, d[0], d[1], place, d[2], d[3], scrape_time))
    writer.writerows(lines)

print len(visited)
print 'codes visited ' + str(len(DONE_CODES))

if True:
  exit()


# STEP 2: Go through each link and extract the relevant information.

def count_munis():
  contents = file(country_url).read()
  tree = etree.HTML(contents)
  state_links = {}
  for elem in tree.xpath('//li[@class="region-nav-item"]/a'):
    state_links[elem.text] = url_path + elem.get('href')
  munis = set()
  for (state, link) in state_links.iteritems():
    contents = file(link).read()
    tree = etree.HTML(contents)
    muni_links = {}
    for elem in tree.xpath('//li[@class="region-nav-item"]/a'):
      muni_links[elem.text] = elem.get('href')
    print state + ': ' + str(len(muni_links))
    for link in muni_links.values():
      if link in munis:
        print 'REPEATED: ' + link
      munis.add(link)

  return munis

if True:
  print len(count_munis())
  exit()

# votes is of the form:
#  {<State> -> {<Muni> -> {<Parish> -> {Center -> {<Candidate> -> <votes>}}}}}
votes = {}

# Proposal
# data = { (<code>, <updated_date>) -> <summary> }
# where code is the number in the html file: reg_<code>.html; updated_date is the date the CNE last updated their site.
# Summaries is a dictionary with the following information (keys in spanish because i don't want to translate cne terms):
# State, Municipality, Parish, Center, Table. These can be hierarchichally null. If any are null, then values are aggregated.
# Candidate, Parties (comma-separated list), Votes, Votes_per_party (comma-separated list, in the same order as parties). These can be absent in lines to indicate 'ficha tenica' values
# For ficha tecnica, includes all data in ficha tecnica (9 values)
# Lastly, include URL from where to gather the info, as well as scrape_date.

# Restrict data to "ALCALDE" only. There should be 1 per real municipality (335) + Caracas and Apure districts = 337.
# Some of the links are repeated (two links to the same muni from different 'states')
# By adding the links off the state pages, we get a sum of 342. But Caracas "district" overcounts 5, and has 1 real one => 338. And Apure "district" overcounts 2 and adds 1, so total => 337... Still 2 off..

iterend = 1000
state_links = extract_nav_links(parse(country_url))
for state_link in itertools.islice(state_links, 0, iterend):
  print "Processing STATE " + state_link
  state_tree = parse(url_root + state_links[state_link])
  muni_links = extract_nav_links(state_tree)
#  muni_dict = defaultdict(dict)
#  # muni dict holds details per muni and state totals (which is muni-aggregated totals)
#  muni_dict["total"] = extract_votes(state_tree)
  for muni_link in itertools.islice(muni_links, 0, iterend):
    print "\tProcessing MUNI " + muni_link
    muni_tree = parse(url_root + muni_links[muni_link])
    parish_links = extract_nav_links(muni_tree)
#    muni_dict[muni_link]["total"] = extract_votes(muni_tree)
    for parish in itertools.islice(parish_links, 0, iterend):
      print "\t\tProcessing PARISH " + parish
      parish_tree = parse(url_root + parish_links[parish])
      center_links = extract_nav_links(parish_tree)
#      muni_dict[muni_link][parish] =  {}
#      muni_dict[muni_link][parish]["total"] = extract_votes(parish_tree)
      for center in itertools.islice(center_links, 0, iterend):
        print "\t\t\tProcessing CENTER: " + center
        parse(url_root + center_links[center])
#        muni_dict[muni_link][parish][center]  = extract_votes(parse(url_root + center_links[center]))
#  votes[state_link] = muni_dict

#write_to_file(votes)


