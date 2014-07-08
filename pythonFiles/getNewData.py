
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
  page = requests.get(xmlLink)
  
  f = StringIO.StringIO() 
  f.write(page.content)
  
  # extract the data
  extracted = extract_zip(f)
  print "Extracted file: " + extracted.keys()[0]
  d = extracted.values()[0]

  # extract the data from xml file (there also is a method called iterfind)
  ids = []
  root = ET.fromstring(d)
  for row in root.findall('row'):
    id = row.find('APPLICATION_ID').text
    ids.append(id)

# missing now is automatic header detection - that is - child detection ... 
# I could use regular expressions, but that seems unelegant and laborious. 
# further understanding of xml required, also - I'm not sure what I am doing.
# also include wait interval to avoid getting blocked from website
