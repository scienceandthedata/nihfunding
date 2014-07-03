
# Import required modles
#--------------------------------------------
import pandas as pd
import numpy as np
import sqlite3 as lite
import sys
import os
from pandas import DataFrame, Series
import argparse



# Trying to understand data to figure out how to construct the db
#--------------------------------------------

# Look here for questions about columns
# http://exporter.nih.gov/about.aspx

# headers = data.columns.values.tolist()

""" dataStruct = {}
for header in headers:
  tmp = {}
  tmp['values'] = list(data[header].unique())
  tmp['count'] = len(data[header].unique())
  dataStruct[header] = tmp """

# Info on types of grants:
# http://grants.nih.gov/grants/funding/ac_search_results.htm
# Does this match up with types of grants we find in our data file?

# Full project number gives us a lot of information - whether the successful application was once amended.
# http://www.nimh.nih.gov/funding/grant-writing-and-application-process/research-funding-frequently-asked-questions-faqs.shtml#content_5
# Core project number seems to be a part of the sull number (without prefix and suffix)
# serial also part of full number
# TABLE
# full project to core to suffix to serial to program office (extract from full is not in data)
# TABLE
# also, table for abbreviation NIH institute and name

# ALSO, think about the applications that start with 5 in the full project number
# these are continuations not even subject to peer review?
# perhaps we need to get a filter for those, 1, 2, vs. 5

# what does suport year mean = values from 1 to in the 50s

# FOA number - funding opportunity accouncement
# one FOA has almost always the same ACTIVITY (e.g. R01, K99) BUT NOT ALWAYS
# how to handle?
"""foas = data.FOA_NUMBER.drop_duplicates()
foasToGrant = {}
for foa in foas:
  foasToGrant[foa]=data.ACTIVITY[data.FOA_NUMBER==foa]"""

# Could we get descriptions of NIH institutes, FOAs? Would those be interesting - like -
# what title (grant) was accepted for a FOA?

# FOAs over the years?

# PHR has long text fragments in it

# officers for almost always - BUT NOT ALWAYS - for only one NIH institute
"""officers = data.PROGRAM_OFFICER_NAME.drop_duplicates()
for officer in officers:
  try:
    print officer + "\n"
    print set(data.IC_NAME[data.PROGRAM_OFFICER_NAME==officer].values)
  except TypeError:
    continue"""

# Special emphasis splits up in different panels
#http://public.csr.nih.gov/StudySections/SpecialEmphasis/Pages/default.aspx


if __name__ == "__main__":

  #--------------------------------------------
  # Parse input
  #--------------------------------------------  
  
  # parser = argparse.ArgumentParser(description = 'Create the NIH DB from CSV files.')
  # parser.add_argument()

  #--------------------------------------------
  # Load data
  #--------------------------------------------  

  # determine current working directory
  
  os.chdir('../dataFiles')
  data = pd.read_csv('RePORTER_PRJ_C_FY2011.csv')
  os.chdir('../dataFiles/db') # change to current working directory

  #--------------------------------------------
  # Create table entries for PI id and PI name
  #--------------------------------------------

  def rmSemiPar(x):
    x = x.split(';')[0]
    x = x.split('(')[0]
    return x
  pis = data[['PI_IDS','PI_NAMEs']].drop_duplicates(['PI_IDS'])
  pis = pis.applymap(rmSemiPar)
  entriesPIs = zip(pis.PI_IDS,pis.PI_NAMEs)

  con = None
  try:
    con = lite.connect('nih.db')
    cur = con.cursor()
    print "Construct PI NAMES table ... \n"
    cur.execute("DROP TABLE IF EXISTS pi_names")
    cur.execute("CREATE TABLE pi_names(id TEXT, name TEXT)")
    cur.executemany("INSERT INTO pi_names VALUES(?, ?)", entriesPIs)
    con.commit()
    print "Success ... \n\n"
  except lite.Error, e:
    if con:
      con.rollback()
    print "Error %s:" % e.args[0]
    sys.exit(1)
  finally:
    if con:
      con.close()

  #--------------------------------------------
  # Create table entries for Studysection ID and studysection Name
  #--------------------------------------------

  ss = data[['STUDY_SECTION','STUDY_SECTION_NAME']].drop_duplicates(['STUDY_SECTION'])
  entriesSS = zip(ss.STUDY_SECTION,ss.STUDY_SECTION_NAME)

  con = None
  try:
    con = lite.connect('nih.db')
    cur = con.cursor()
    print "Construct STUDY SECTION NAMES table ... \n"
    cur.execute("DROP TABLE IF EXISTS studysection_names")
    cur.execute("CREATE TABLE studysection_names(id TEXT, name TEXT)")
    cur.executemany("INSERT INTO studysection_names VALUES(?, ?)", entriesSS)
    con.commit()
    print "Success ... \n\n"
  except lite.Error, e:
    if con:
      con.rollback()
    print "Error %s:" % e.args[0]
    sys.exit(1)
  finally:
    if con:
      con.close()

  #--------------------------------------------
  # uni name, city, state, country - join by city as foreign destinations have no zipcode
  #--------------------------------------------

  unis = data[['ORG_NAME', 'ORG_DUNS','ORG_CITY', 'ORG_DISTRICT', 'ORG_STATE', 'ORG_COUNTRY', 'ORG_FIPS']].drop_duplicates(['ORG_NAME', 'ORG_CITY'])
  unis = unis.sort('ORG_NAME')
  unis['UNI_ID'] = range(1,len(unis)+1)
  entriesUnis = zip(unis.UNI_ID, unis.ORG_NAME, unis.ORG_DUNS, unis.ORG_CITY, unis.ORG_DISTRICT, unis.ORG_STATE, unis.ORG_COUNTRY, unis.ORG_FIPS)

  con = None
  try:
    con = lite.connect('nih.db')
    cur = con.cursor()
    print "Construct LOCATIONS table ... \n"
    cur.execute("DROP TABLE IF EXISTS locations")
    cur.execute("CREATE TABLE locations(uni_id INTEGER, name TEXT, duns TEXT, city TEXT, district TEXT, state TEXT, country TEXT, fips TEXT)")
    cur.executemany("INSERT INTO locations VALUES(?, ?, ?, ?, ?, ?, ?, ?)", entriesUnis)
    con.commit()
    print "Success ... \n\n"
  except lite.Error, e:
    if con:
      con.rollback()
    print "Error %s:" % e.args[0]
    sys.exit(1)
  finally:
    if con:
      con.close()

  #--------------------------------------------
  # zipcode, university name - lookup for all entries with zipcodes by name
  #--------------------------------------------

  zips = data[['ORG_NAME', 'ORG_ZIPCODE']].drop_duplicates(['ORG_NAME', 'ORG_ZIPCODE'])
  zips = zips.sort('ORG_NAME')
  zips['_ID'] = range(1,len(zips)+1) # create unique ID for db
  entriesZips = zip(zips._ID, zips.ORG_NAME, zips.ORG_ZIPCODE)

  con = None
  try:
    con = lite.connect('nih.db')
    cur = con.cursor()
    print "Construct ZIPs table ... \n"
    cur.execute("DROP TABLE IF EXISTS zips")
    cur.execute("CREATE TABLE zips(id INTEGER, zip TEXT, uni_duns TEXT)")
    cur.executemany("INSERT INTO zips VALUES(?, ?, ?)", entriesZips)
    con.commit()
    print "Success ... \n\n"
  except lite.Error, e:
    if con:
      con.rollback()
    print "Error %s:" % e.args[0]
    sys.exit(1)
  finally:
    if con:
      con.close()

