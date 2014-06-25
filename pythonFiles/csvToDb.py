import pandas as pd
import sqlite3 as lite
import sys

#--------------------------------------------

# example file
data = pd.read_csv('RePORTER_PRJ_C_FY2011.csv')

"""# create tuple for data base

def make_lower_case(x):
  try:
    return x.lower()
  except AttributeError:
    return

data.ORG_CITY = data.ORG_CITY.apply(make_lower_case)
cities = data.ORG_CITY.unique()"""


# think about way to make this more efficient
duns = data.ORG_DUNS.unique() # 9 digit unique business identifier
names = []
for dun in duns:
  try:
    names.append(tuple([dun, data.ORG_NAME[data.ORG_DUNS == dun].unique()[0]]))
  except IndexError:
    names.append(tuple([dun, 'no name']))
names = tuple(names) # as input for SQL query


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


