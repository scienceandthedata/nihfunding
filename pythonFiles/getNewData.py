
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

# extracts data from xml - goes to lowest level and extracts tag and text
# returns tag and text as a tuple (returns list of tuple)
def extractData(nodes,data):
  for node in nodes:
    nchildren = node.getchildren()
    if nchildren:
      extractData(nchildren,data)
    else:
      data.append((node.tag, node.text))
  return data

# extracts all unique headers in file
def extractHeader(nodes,header):
  for node in nodes:
    nchildren = node.getchildren()
    if nchildren:
      extractHeader(nchildren,header)
    else:
      if node.tag not in header:
        header.append(node.tag)
  return header

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
  # extract all links to zip file containing xml data from NIH website, parse, and save as csv
  #--------------------------------

  # get all data files (xml data as zip files)
  for xmlLink in xmlLinks[7:8]:
    page = requests.get(xmlLink) # returns zip file - for publications, this returns a 404 error - not sure why, links seem valid
    
    # make f a file like object and write the data of page 
    # to run processes in memory, necessary because
    # zipfile expects file object
    f = StringIO.StringIO() 
    f.write(page.content)
    
    # extract the data
    extracted = extract_zip(f)
    print "Extracted file: " + extracted.keys()[0]
    root = ET.fromstring(extracted.values()[0]) # this step takes a long time ...

    # data to dictionary
    print "Parsing xml data ... \n"
    
    # find "columns"
    header = [] 
    header = extractHeader(root.findall('row'),header)

    # extract data (as tuple: key, value)
    data = []
    data = extractData(root.findall('row'),data)

    # make dict for each "row"
    rowStart = header[0]
    allData = []
    row = None
    for i,j in data:
      if i == rowStart:
        if row:
          allData.append(row)
        row = {}
        row[i] = j
      elif i in row:
        row[i] = row[i]+';'+j
      else:
          row[i] = j
    allData.append(row) # append final row

    # Reorder data and put in missing values in rows with missing entries
    toDF = []
    for row in allData:
      entry = []
      for head in header:
        if head in row.keys():
          entry.append(row[head])
        else:
          entry.append('NULL')
      toDF.append(entry)

    # convert to dataframe
    DATA = DataFrame(toDF,columns=header)

    print "Saving data ... \n"
    filename = xmlLink.split('/')[-1].split('.')[0] + '.csv'
    DATA.to_csv(filename) # change to data path eventually - file conversion issues ...

# eventually create file of all downloaded data, check in file whether there is a new dataset and add only new data to data base.
# with data base, parsing may be less of an issue, as we will not have to parse all data into a single file
# have optional input which allows to specify to reparse an already existing file (all or specific file)






