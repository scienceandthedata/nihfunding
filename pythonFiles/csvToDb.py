
# Import required modles
#--------------------------------------------
import pandas as pd
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
countsPerColumn = {}
countsPerColumn['all'] = len(data)
for header in headers:
  countsPerColumn[header] = len(data[header].unique())

# think about way to make this more efficient
duns = data.ORG_DUNS.unique() # 9 digit unique business identifier
names = []
for dun in duns:
  try:
    names.append(tuple([dun, data.ORG_NAME[data.ORG_DUNS == dun].unique()[0]]))
  except IndexError:
    names.append(tuple([dun, 'no name']))
names = tuple(names) # as input for SQL query

# zip to city to state to country


# Create table entries for PI id and PI name
# Note: some have (contact) after - leave for now
piIds = data.PI_IDS.unique()
entries = []
for pi in piIds:
  name = data.PI_NAMEs[data.PI_IDS == pi].iloc[0].split(';')[0]
  pi = pi.split(';')[0]
  entries.append(tuple([pi,name]))

piIds = piIds.merge(data[['PI_IDS', 'PI_NAMEs']],on='PI_IDS', how='left')
piIds.PI_IDS = piIds.PI_IDS.apply(lambda x: x.split(';')[0])
piIds.PI_IDS = piIds.PI_IDS.apply(lambda x: x.split('(')[0]) 
piIds.PI_NAMEs = piIds.PI_NAMEs.apply(lambda x: x.split(';')[0])
piIds.PI_NAMEs = piIds.PI_NAMEs.apply(lambda x: x.split('(')[0]) 

subset.PI_IDS = subset.PI_IDS.apply(lambda x: x.split(';')[0])
subset.PI_NAMEs = subset.PI_NAMEs.apply(lambda x: x.split(';')[0])

pis = [tuple(x) for x in subset.values]

# Create table entries for Studysection ID and studysection Name
# Note: some have (contact) after - leave for now
subset = data[['STUDY_SECTION', 'STUDY_SECTION_NAME']]
studysecs = [tuple(x) for x in subset.values]

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


