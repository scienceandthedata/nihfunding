
from lxml import html
import requests
from bs4 import BeautifulSoup
import zipfile 
import StringIO

from xml.etree import ElementTree as ET

#--------------------------------
# extract all links to zip file containing xml data from NIH website
#--------------------------------

page = requests.get('http://exporter.nih.gov/ExPORTER_Catalog.aspx')
soup = BeautifulSoup(page.text)

xmlLinks = []
for hrefs in soup.find_all('a'):
  link = hrefs.get('href')
  try:
    if 'XMLData' in link:
      xmlLinks.append("http://exporter.nih.gov/"+link)
  except TypeError:
    print link

#--------------------------------
# extract all links to zip file containing xml data from NIH website
#--------------------------------

# helper function to extract zip files
def extract_zip(input_zip):
    input_zip = zipfile.ZipFile(input_zip)
    return {i: input_zip.read(i) for i in input_zip.namelist()}

# get all data files (xml data as zip files)
for xmlLink in xmlLinks:
  page = requests.get(xmlLinks) # returns zip file
  
  # make f a file like object and write the data of page 
  # to run processes in memory, necessary because
  # zipfile expects file object
  f = StringIO.StringIO() 
  f.write(page.content)
  
  # extract the data
  extracted = extract_zip(f)
  print "Extracted file: " + extracted.keys()[0]
  d = extracted.values()[0]

  # Look at data currently string format
  print d

  # parses xml from string
  root = ET.fromstring(d)

# in development -----------------

# extract the data from xml file - adjust to prevent overwriting ...
for row in root.findall('row'):
  children = row.getchildren()
  
  dataLine = {}
  for child in children:
      dataLine[child.tag] = child.text


# generator function
def iterparent(tree):
  for parent in tree.getiterator():
      for child in parent:
          yield parent, child

for parent, child in iterparent(tree):
    ... work on parent/child tuple

parent_map = dict((c, p) for p in root.getiterator() for c in p)

a = root.findall("row/*")[2].text

# https://docs.python.org/2/library/xml.etree.elementtree.html
# http://infohost.nmt.edu/tcc/help/pubs/pylxml/web/Element-children.html

# missing now is automatic header detection - that is - child detection ... 
# I could use regular expressions, but that seems unelegant and laborious. 
# further understanding of xml required, also - I'm not sure what I am doing.
# also include wait interval to avoid getting blocked from website
