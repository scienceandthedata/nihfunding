from lxml.html import parse
from urllib2 import urlopen
import json
import pandas as pd

# this gets all the table elements from a url 
def gettables(url):
    parsed = parse(urlopen(url))
    doc = parsed.getroot()
    tables = doc.findall('.//table')
    return tables

# find all the tables in the page
# each table has rows with tr tag
# extract text data with td tag 
def unpacktable(table,kind='td'):
    allrows = []
    rows = table.findall('.//tr')
    for row in rows:
        elts = row.findall('.//%s' % kind)
        rowcontent = [val.text_content() for val in elts]
        allrows.append(rowcontent)
    return allrows

#----------------------------------------------------------------

# this website has mechanism and funding description for 
# Non-NRSA Fellowships, Training, and Education Grant Funding Opportunities
url1 = 'http://grants.nih.gov/training/F_files_non_nrsa.htm'
# get tables and parse the main table of relevance 
tables = gettables(url1)
allrows = unpacktable(tables[1])

# put stuff into a dictionary
mechanism = dict()
for row in allrows[1:]:
    mec = row[0].replace('\n', '').replace('\t', '')
    desc = row[1].replace('\n', '').split('\t\t\t')
    mechanism[mec] = filter(None, desc)

# write things into a json
with open('F_files_non_nrsa.json','w') as outfile:
    json.dump(mechanism,outfile)

#----------------------------------------------------------------
# activity code search results 
# TODO: should probably also add link urls into the table 
url2 = 'http://grants.nih.gov/grants/funding/ac_search_results.htm'
tables = gettables(url2)
allrows = unpacktable(tables[4])
# get the headers for the table
allrowsheader = unpacktable(tables[4],'th')
allrowsheader = filter(None, allrowsheader)
headers = [h.replace('\t', '').replace('\r', '').replace('\n', '') for h in allrowsheader[0]]

# create a list of dictionaries 
# wow this was a pain to figure out 
# see this guy http://stackoverflow.com/questions/10715965/add-one-row-in-a-pandas-dataframe
rows_list = []
for row in allrows[1:]:
    # get rid of junk in last cell
    row[4] = row[4].replace('\t', '').replace('\r', '').replace('\n', '')
    # put new row into a dictionary 
    rowdict = {}
    for i, r in enumerate(row): 
        rowdict[headers[i]] = r
    # append to the list 
    rows_list.append(rowdict)

# populate the table into a data frame
ac_codes = pd.DataFrame(rows_list) 

# write things into a json
# with open('ac_search_results.json','w') as outfile:
#     json.dump(ac_codes.to_json(),outfile)