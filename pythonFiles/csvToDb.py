
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

# great argparse tutorial: https://docs.python.org/2/howto/argparse.html

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
# http://public.csr.nih.gov/StudySections/SpecialEmphasis/Pages/default.aspx

#--------------------------------------------
# Function definitions
#--------------------------------------------  

def insertIntoDB(dbName, tableName, queries, entries):
  con = None
  try:

    print "Connect to database " + dbName + "..."
    con = lite.connect(dbName)
    cur = con.cursor()

    print "Construct table " + tableName + "..."
    queries(cur, tableName, entries)
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
# Run when called from command line
#--------------------------------------------  

if __name__ == "__main__":

  #--------------------------------------------
  # Parse input
  #--------------------------------------------  
  
  parser = argparse.ArgumentParser(description = 'Create the NIH DB from CSV files.')
  parser.add_argument("dbName", help = "Enter the name of the data base.", type = str)
  args = parser.parse_args()
  dbName = args.dbName

  #--------------------------------------------
  # Load data
  #--------------------------------------------  

  os.chdir('../dataFiles')
  data = pd.read_csv('RePORTER_PRJ_C_FY2011.csv')
  os.chdir('../dataFiles/db') # db location

  #--------------------------------------------
  # Create table entries for PI id and PI name
  #--------------------------------------------

  def rmSemiPar(x):
    x = x.split(';')[0]
    x = x.split('(')[0]
    return x
  d = data[['PI_IDS','PI_NAMEs']].drop_duplicates(['PI_IDS'])
  d = d.applymap(rmSemiPar)
  entries = zip(d.PI_IDS,d.PI_NAMEs)

  def queries(cur, tableName, entries):
    query = "DROP TABLE IF EXISTS " + tableName
    cur.execute(query)
    query = "CREATE TABLE " + tableName + "(id TEXT, name TEXT)"
    cur.execute(query)
    query = "INSERT INTO " + tableName + " VALUES(?, ?)"
    cur.executemany(query, entries)

  insertIntoDB(dbName, 'piNames', queries, entries)

  #--------------------------------------------
  # Create table entries for Studysection ID and studysection Name
  #--------------------------------------------

  d = data[['STUDY_SECTION','STUDY_SECTION_NAME']].drop_duplicates(['STUDY_SECTION'])
  entries = zip(d.STUDY_SECTION,d.STUDY_SECTION_NAME)

  def queries(cur, tableName, entries):
    query = "DROP TABLE IF EXISTS " + tableName
    cur.execute(query)
    query = "CREATE TABLE " + tableName + "(id TEXT, name TEXT)"
    cur.execute(query)
    query = "INSERT INTO " + tableName + " VALUES(?, ?)"
    cur.executemany(query, entries)

  insertIntoDB(dbName, 'studySectionNames', queries, entries)

  #--------------------------------------------
  # uni name, city, state, country - join by city as foreign destinations have no zipcode
  #--------------------------------------------

  d = data[['ORG_NAME', 'ORG_DUNS','ORG_CITY', 'ORG_DISTRICT', 'ORG_STATE', 'ORG_COUNTRY', 'ORG_FIPS']].drop_duplicates(['ORG_NAME', 'ORG_CITY'])
  d = d.sort('ORG_NAME')
  d['UNI_ID'] = range(1,len(d)+1)
  entries = zip(d.UNI_ID, d.ORG_NAME, d.ORG_DUNS, d.ORG_CITY, d.ORG_DISTRICT, d.ORG_STATE, d.ORG_COUNTRY, d.ORG_FIPS)

  def queries(cur, tableName, entries):
    query = "DROP TABLE IF EXISTS " + tableName
    cur.execute(query)
    query = "CREATE TABLE " + tableName + "(uni_id INTEGER, name TEXT, duns TEXT, city TEXT, district TEXT, state TEXT, country TEXT, fips TEXT)"
    cur.execute(query)
    query = "INSERT INTO " + tableName + " VALUES(?, ?, ?, ?, ?, ?, ?, ?)"
    cur.executemany(query, entries)

  insertIntoDB(dbName, 'uniLocations', queries, entries)

  #--------------------------------------------
  # zipcode, university name - lookup for all entries with zipcodes by name
  #--------------------------------------------

  # change to project ID to zipcode (probably not accessed often)
  d = data[['ORG_NAME', 'ORG_ZIPCODE']].drop_duplicates(['ORG_NAME', 'ORG_ZIPCODE'])
  d = d.sort('ORG_NAME')
  d['_ID'] = range(1,len(d)+1) # create unique ID for db
  entries = zip(d._ID, d.ORG_NAME, d.ORG_ZIPCODE)

  def queries(cur, tableName, entries):
    query = "DROP TABLE IF EXISTS " + tableName
    cur.execute(query)
    query = "CREATE TABLE " + tableName + "(id INTEGER, zip TEXT, uni_duns TEXT)"
    cur.execute(query)
    query = "INSERT INTO " + tableName + " VALUES(?, ?, ?)"
    cur.executemany(query, entries)

  insertIntoDB(dbName, 'zips', queries, entries)


