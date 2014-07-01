
# Import required modles
#--------------------------------------------
import pandas as pd
import numpy as np
import sqlite3 as lite
import sys
import os
from pandas import DataFrame, Series

# Load the data
#--------------------------------------------
os.chdir('../dataFiles')
data = pd.read_csv('RePORTER_PRJ_C_FY2011.csv')
os.chdir('../pythonFiles')

# Trying to understand data to figure out how to construct the db
#--------------------------------------------

headers = data.columns.values.tolist()

dataStruct = {}
for header in headers:
  tmp = {}
  tmp['values'] = list(data[header].unique())
  tmp['count'] = len(data[header].unique())
  dataStruct[header] = tmp

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

# PHR has long text fragments in it

# officers for almost always - BUT NOT ALWAYS - for only one NIH institute
officers = data.PROGRAM_OFFICER_NAME.drop_duplicates()
for officer in officers:
  try:
    print officer + "\n"
    print set(data.IC_NAME[data.PROGRAM_OFFICER_NAME==officer].values)
  except TypeError:
    continue

# Special emphasis splits up in different panels
#http://public.csr.nih.gov/StudySections/SpecialEmphasis/Pages/default.aspx


# Creating the entries
#--------------------------------------------

# Create table entries for PI id and PI name
def rmSemiPar(x):
  x = x.split(';')[0]
  x = x.split('(')[0]
  return x
pis = data[['PI_IDS','PI_NAMEs']].drop_duplicates(['PI_IDS'])
pis = pis.applymap(rmSemiPar)
entriesPIs = zip(pis.PI_IDS,pis.PI_NAMEs)

# Create table entries for Studysection ID and studysection Name
ss = data[['STUDY_SECTION','STUDY_SECTION_NAME']].drop_duplicates(['STUDY_SECTION'])
entriesSS = zip(ss.STUDY_SECTION,ss.STUDY_SECTION_NAME)

# uni name, city, state, country - join by city as foreign destinations have no zipcode
unis = data[['ORG_NAME', 'ORG_DUNS','ORG_CITY', 'ORG_STATE', 'ORG_COUNTRY']].drop_duplicates(['ORG_NAME', 'ORG_CITY'])
unis = unis.sort('ORG_NAME')
unis['UNI_ID'] = range(1,len(unis)+1)
entriesUnis = zip(unis.UNI_ID, unis.ORG_NAME, unis.ORG_DUNS, unis.ORG_CITY, unis.ORG_STATE, unis.ORG_COUNTRY)

# zipcode, university name - lookup for all entries with zipcodes by name
zips = data[['ORG_NAME', 'ORG_ZIPCODE']].drop_duplicates(['ORG_NAME', 'ORG_ZIPCODE'])
zips = zips.sort('ORG_NAME')
zips['_ID'] = range(1,len(zips)+1) # create unique ID for db
entriesZips = zip(zips._ID, zips.ORG_NAME, zips.ORG_ZIPCODE)

# Connecting to db and inserting values
#--------------------------------------------

con = None

try:
  con = lite.connect('nih.db')
  cur = con.cursor()

  cur.execute("DROP TABLE IF EXISTS institute_names")
  cur.execute("CREATE TABLE institute_names(DUNS TEXT, Name TEXT)")
  cur.executemany("INSERT INTO institute_names VALUES(?, ?)", names)
  con.commit()

except lite.Error, e:

  if con:
    con.rollback()

  print "Error %s:" % e.args[0]
  sys.exit(1)

finally:
  
  if con:
    con.close()


