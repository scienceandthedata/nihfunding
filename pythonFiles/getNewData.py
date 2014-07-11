
from lxml import html
import requests
from bs4 import BeautifulSoup
import zipfile 
import StringIO
from xml.etree import ElementTree as ET
import sys
import os
import argparse
import csv
from pandas import DataFrame
import pandas as pd

#--------------------------------------------
# Functions
#--------------------------------------------  

# helper function to extract zip files
def extract_zip(input_zip):
    input_zip = zipfile.ZipFile(input_zip)
    return {i: input_zip.read(i) for i in input_zip.namelist()}

#--------------------------------------------
# Main
#--------------------------------------------  

if __name__ == "__main__":

  #--------------------------------------------
  # Parse input
  #--------------------------------------------  
  
  parser = argparse.ArgumentParser(description = 'Download data from NIH website: http://exporter.nih.gov/ExPORTER_Catalog.aspx')
  parser.add_argument("dataToDownload", help = "Enter what type of data to download: projects, abstracts, publications, or linkTables", type = str)
  args = parser.parse_args()
  typeData = args.dataToDownload

  url = 'http://exporter.nih.gov/ExPORTER_Catalog.aspx'
  if typeData == 'projects':
    pass
  elif typeData == 'abstracts':
    url += '?sid=0&index=1'
  elif typeData == 'publications':
    url += '?sid=1&index=2'
  elif typeData == 'linkTables':
    url += '?sid=3&index=4'
  else:
    print 'No such data: ' + typeData
    sys.exit()

  #--------------------------------
  # extract all links to zip file containing xml data from NIH website
  #--------------------------------

  page = requests.get(url)
  soup = BeautifulSoup(page.text)

  xmlLinks = []
  for hrefs in soup.find_all('a'):
    link = hrefs.get('href')
    try:
      if 'XMLData' in link:
        xmlLinks.append("http://exporter.nih.gov/"+link)
    except TypeError:
      pass # only happens for None (verified)

  #--------------------------------
  # extract all links to zip file containing xml data from NIH website and save as csv
  #--------------------------------

  # get all data files (xml data as zip files)
  for xmlLink in xmlLinks[1:2]:
    page = requests.get(xmlLink) # returns zip file
    
    # make f a file like object and write the data of page 
    # to run processes in memory, necessary because
    # zipfile expects file object
    f = StringIO.StringIO() 
    f.write(page.content)
    
    # extract the data
    extracted = extract_zip(f)
    print "Extracted file: " + extracted.keys()[0]
    root = ET.fromstring(extracted.values()[0]) # this step takes a long time ...

    # data to dictionary (row numbers match previously downloaded files, PIS contains PI_IDs and PI_Names)
    print "Parsing xml data ... \n"
    data = {}
    for row in root.findall('row'):
      children = row.getchildren()
      
      for child in children:
        grandchildren = child.getchildren()

        if grandchildren: # sometimes, they need to be added, like for terms and sometimes deparate columns, like for PIS and one other case (try to find)
          # basically create one column by forming list of all identical tags but not if different tags.
          # also check if there are any further generations ... - almost there.
          entry = []
          for grandchild in grandchildren:
            entry.append(grandchild.text)
        else:
          entry = child.text

        # add entries to dictionary
        if child.tag in data:
          data[child.tag].append(entry)

        else:
          data[child.tag] = []
          data[child.tag].append(entry)

    # save all data (ugly but does SOMTIMES work) :s
    """UnicodeEncodeError: 'ascii' codec can't encode character u'\xa0' in position 0: ordinal not in range(128)"""

    print "Saving data ... \n"
    filename = xmlLink.split('/')[-1].split('.')[0] + '.csv'
    data = DataFrame(data)
    data.to_csv(filename) # change to data path eventually

# eventually create file of all downloaded data, check in file whether there is a new dataset and add only new data to data base.
# with data base, parsing may be less of an issue, as we will not have to parse all data into a single file
# have optional input which allows to specify to reparse an already existing file (all or specific file)






