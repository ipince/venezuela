#!/usr/bin/python

import codecs
import os
import urllib2
import itertools
from collections import defaultdict
from lxml import etree


def cached_url(url):
  return os.path.join("htmlcache", url.replace("/", "_").replace(":", "_"))

def parse(url):
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

def extract_nav_links(tree):
  BAD_LINKS = ['EMBAJADA', 'INHOSPITOS']
  links = {}
  for elem in tree.xpath('//li[@class="region-nav-item"]/a[@id="region_ref"]'):
    # gives you UTF-8 encoded obj of type 'str'
    txt = codecs.encode(elem.text, 'utf-8')
    if (txt not in BAD_LINKS):
      links[txt] = elem.get("href")
  #print "\tExtracted links: " + str(links)
  return links
'''
def extract_candidate_votes(tree):
  votes = {}
  for tr in tree.xpath('//tr[@class="tbsubtotalrow"]'):
    cells = tr.xpath('td[@class="lightRowContent"]/span')
    votes[codecs.encode(cells[0][0].text, 'utf-8')] = str(cells[1].text).replace('.', '')
  #print "\tExtracted candidate votes: " + str(votes)
  return votes

def extract_total_votes(tree):
  totals = {}
  for row in tree.xpath('//div[@id="fichaTecnica"]//tr[@class="tblightrow"]'):
    keys = row.xpath('td/span/b')
    values = row.xpath('td[last()]')
    for i in range(len(keys)):
      if (values[i].text):
        totals[codecs.encode(keys[i].text, 'utf-8')] = str(values[i].text).replace('.', '')
  #print "\tExtracted totals: " + str(totals)
  return totals

def extract_votes(tree):
  d1 = extract_candidate_votes(tree)
  d2 = extract_total_votes(tree)
  return defaultdict(lambda : 'N/A', d1.items() + d2.items())

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

url_root = 'http://www.cne.gob.ve/resultado_presidencial_2012/r/1/';
country_url = url_root + 'reg_000000.html'

# votes is of the form:
#  {<State> -> {<Muni> -> {<Parish> -> {Center -> {<Candidate> -> <votes>}}}}}
votes = {}

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


