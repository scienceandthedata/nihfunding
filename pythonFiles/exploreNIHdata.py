# import modules
import pandas as pd # import as pd conventional
from pandas import DataFrame, Series
import numpy as np # import as np conventional
import os
import matplotlib.pyplot as plt
import re
import json

# User defined functions
#----------------------------------------------------------------

def barGraph(xvals,yvals,width,xTick,xLabel,yLabel,bottomAdjust,saveFigure=0):
	fig, ax = plt.subplots()
	rects = ax.bar(xvals,yvals,width,color='r')
	ax.set_ylabel(yLabel)
	ax.set_title(xLabel)
	ax.set_xticks(xvals)
	ax.set_xticklabels(xTick)
	for tick in ax.xaxis.get_major_ticks():
	    tick.label.set_fontsize(8) 
	    tick.label.set_rotation('vertical')
	if bottomAdjust != 0:
		fig.subplots_adjust(bottom=bottomAdjust)
	plt.show()
	if isinstance(saveFigure,str):
		fig.set_size_inches(18.5,10.5)
		plt.savefig(saveFigure,dpi=100)

def loadData_fromOriginal(nrFiles,saveFile):
	
	# makes list of all files with 'RePORTER' in name
	files = [f for f in os.listdir(dataPath) if os.path.isfile(f) and 'RePORTER' in f and '.csv' in f]
	
	# with string input, loads all files, otherwise specified number
	if isinstance(nrFiles,str):
		pass
	elif nrFiles>len(files):
		print 'Limit # files to load to less than: ' + str(len(files)) + '\n'
		return
	else:
		files = files[0:nrFiles]

	# read in first file (and remove file name from list), automatically detects correct headers for columns
	print 'Loading data: ' + files[0] + '\n'
	data = pd.read_csv(files.pop(0))

	# append all remaining data
	for file in files:
		print 'Loading data: ' + file + '\n'
		newData = pd.read_csv(file)
		data = data.append(newData)

	if saveFile:
		data.to_csv('NIH_data.csv')

	return data


# Load data
#----------------------------------------------------------------

# Current directory
workingPath = os.getcwd()

# Set path to figures
figurePath = '/Users/Friederike/Dropbox/data pirates/NIH-projectFiles/figures'

# Set path to data:
dataPath = '/Users/Friederike/Dropbox/data pirates/NIH-projectFiles/dataFiles'

# get a list of all files with '.csv' in filename in the data directory (as comprehension)
os.chdir(dataPath)

# load data from individual .csv files
data = loadData_fromOriginal(2,0)

# load data from consolidated file
try:
	data = pd.read_csv('NIH_data.csv',nrows = 10000)
except IOError:
	print 'No such file'


# Some graphs
#----------------------------------------------------------------

# nr grants per states
xvals = range(0,len(data.ORG_STATE.value_counts()))
yvals = data.ORG_STATE.value_counts()
width = 0.5
xTick = tuple(data.ORG_STATE.value_counts().index)
xLabel = 'state'
yLabel = 'count'
barGraph(xvals,yvals,width,xTick,xLabel,yLabel,0,'states.png')

# money per state?

# type grant
xvals = range(0,len(data.ACTIVITY.value_counts()))
yvals = data.ACTIVITY.value_counts()
width = 0.5
xTick = tuple(data.ACTIVITY.value_counts().index)
xLabel = 'grant type'
yLabel = 'count'
barGraph(xvals,yvals,width,xTick,xLabel,yLabel,0,'type.png')

# PIs per name (probably better by PI id?)
dfPis = data.PI_NAMEs.dropna()
dfPis = dfPis.apply(lambda x: x.lower())
dfPis = dfPis.apply(lambda x: x.split(';')[0])
dfPis = dfPis.apply(lambda x: x.split('.')[0])

valDisplay = 30
xvals = range(0,len(dfPis.value_counts()[1:1+valDisplay]))
yvals = dfPis.value_counts()[0:valDisplay]
xTick = tuple(dfPis.value_counts().index[1:1+valDisplay])
width = 0.5
xLabel = 'PI name'
yLabel = 'count of grants received'
barGraph(xvals,yvals,width,xTick,xLabel,yLabel,0.2,'pis.png')

# StudySections - this may be a better variable for sub-selection than keywords
dfSS = data.STUDY_SECTION_NAME.dropna()
dfSS = dfSS.apply(lambda x: x.lower())

valDisplay = 30
xvals = range(0,len(dfSS.value_counts()[1:1+valDisplay]))
yvals = dfSS.value_counts()[0:valDisplay]
xTick = tuple(dfSS.value_counts().index[1:1+valDisplay])
width = 0.5
xLabel = 'Study Section'
yLabel = 'count of grants received'
barGraph(xvals,yvals,width,xTick,xLabel,yLabel,0.3,'studySections.png')

# money per grant type?

# key words (in one column, separated by ';')
dfKW = data.PROJECT_TERMS.dropna()
keywords = {}
for entry in dfKW:
	entry = entry.split(';')
	for element in entry:
		element = element.lower()
		if element in keywords:
			keywords[element]+=1
		else:
			keywords[element] = 1

# convert back to dataframe
dfKW = DataFrame(keywords.values(), index = keywords.keys(), columns = ['counts'])
dfKW = dfKW.sort('counts',ascending=False)

# plot
valDisplay = 30
xvals = range(0,valDisplay)
yvals = array(dfKW.iloc[1:1+valDisplay])
xTick = tuple(dfKW.index[1:1+valDisplay])
width = 0.5
xLabel = 'keyword'
yLabel = 'Count'
bottomAdjust = 0.2
saveFigure = 'keywords.png'
barGraph(xvals,yvals,width,xTick,xLabel,yLabel,bottomAdjust,saveFigure)

# Show count for vision - just for fun
print 'Vision: ' + str(keywords['vision']) + '\n'

# what does support year stand for? Values range from 1 to 37, numbers are descreasing?

# output as json for d3
#---------------------------------------------------------------------------------------

allData = []
states = sorted(list(data.ORG_STATE.value_counts().index))
values = data.ORG_STATE.value_counts()
meanIncome = data['TOTAL_COST'].groupby(data.ORG_STATE).mean()

for state in states:
	stateData = {}
	stateData['state'] = state
	countData = {}
	countData['count'] = values[state]
	countData['logCount'] = math.log(values[state])
	stateData['counts'] = countData
	moneyData = {}
	moneyData['meanIncome'] = meanIncome[state]
	moneyData['logMeanIncome'] = math.log(meanIncome[state])
	stateData['money'] = dict3
	allData.append(dict1)

tmp = {}
tmp['data'] = allData

with open("nih_states.json", "w") as outfile:
    json.dump(tmp, outfile, sort_keys=True, indent=2)

"""

# information missing in particular in earlier years
#RO1data.fillna('Missing')

data['ORG_COUNTRY'].value_counts()
data.groupby('ORG_COUNTRY').size()
data.groupby('ORG_COUNTRY').TOTAL_COST.sum()

RO1byCountryAndIC = RO1data.pivot_table(rows='ORG_COUNTRY',cols='IC_NAME',aggfunc='size')
RO1countryCount.plot(kind='barh')

#RO1data.to_csv('RO1data.csv')
#RO1countryCount.to_csv('countryCount.csv')
#RO1byCountryAndIC.to_csv('RO1byCountryAndIC.csv')
"""

""" Nice example files:
http://wrobstory.github.io/2013/04/python-maps-choropleth.html
http://bl.ocks.org/mbostock/4060606
"""

# look at the distribution of application type for RO1 grants
# R01 accounts for about 35.7% of the grants 
# mostly type 5 = Non-competing continuation
# ---------------------------------------------------------
appIDs = data.APPLICATION_TYPE[data.ACTIVITY=='R01'].astype(int)
xvals = range(0,len(unique(appIDs)))
yvals = appIDs.value_counts()
xTick = tuple(appIDs.value_counts().index)
barGraph(xvals,yvals,0.5,xTick,'application type','count',0,'R01_apptype.png')


# tally up the sums for individual RO1s with the same core project numbers 
# ---------------------------------------------------------
#coreProjNums = unique(data.CORE_PROJECT_NUM[data.ACTIVITY=='R01'])
# projSums = []
# for proj in coreProjNums:
# 	projSums.append(sum(data.TOTAL_COST[data.CORE_PROJECT_NUM==proj]))
R01data = data.ix[data.ACTIVITY=='R01',:]
R01dataCost = R01data.groupby('CORE_PROJECT_NUM').TOTAL_COST.sum().divide(1000000).dropna()
saveFigFlg = False

fig = plt.figure()
ax = fig.add_subplot(2,1,1) # distribution of cost 
ax = R01dataCost.hist(bins=100)
ax.set_ylabel('count')
ax.set_xlabel('total cost (in millions)')
ax.set_title('total cost of R01 core projects')

ax = fig.add_subplot(2,1,2) # ranked cost by individual core projects 
R01dataCost.sort(ascending=False)
plt.plot(R01dataCost,'.',markersize=10) #semilogy
plt.xlim(([-500, len(R01dataCost)+500]))
plt.show()
ax.set_xlabel('rank')
ax.set_ylabel('total cost (in millions)')

if saveFigFlg:
	fig.set_size_inches(18.5,10.5)
	plt.savefig('R01_coreProjectSumCost',dpi=100)


# Cost per by year 
# ---------------------------------------------------------
R01dataCostByYear = R01data.groupby('FY').TOTAL_COST

fig = plt.figure()
ax = fig.add_subplot(2,1,1) # total cost by year 
R01dataCostByYear.sum().divide(1000000).dropna().plot(kind='bar')
ax.set_title('Total R01 Cost by FY (in millions)')

ax = fig.add_subplot(2,1,2) # top 10 percent of grants
R01dataCostByYear.quantile(.90).divide(1000000).dropna().plot(color='g')
R01dataCostByYear.quantile(.50).divide(1000000).dropna().plot(color='k')
R01dataCostByYear.quantile(.10).divide(1000000).dropna().plot(color='r')
plt.ylim((0,0.7))
plt.legend( ('10th', '50th', '90th'),loc='upper left' )
ax.set_title('Quantile Cost by FY (in millions)')

if saveFigFlg:
	fig.set_size_inches(12,8)
	plt.savefig('R01_costByFY',dpi=100)


# Number of grants funded by year 
# ---------------------------------------------------------
fig = plt.figure()
ax = fig.add_subplot(2,2,1)
# total number of new applications per year 
R01data.groupby('FY').APPLICATION_ID.count().plot(kind='bar')
ax.set_title('Total number of grants')
ax.set_ylabel('count')

ax = fig.add_subplot(2,2,2)
# number of new applications per year 
# group grants by core project number and get the first year that it applies 
# get back a data frame indexed by core project number
initCoreByYear = R01data.groupby('CORE_PROJECT_NUM').FY.min()
# reindex so that CORE_PROJECT_NUM and FY are separate columns
initCoreByYear = initCoreByYear.reset_index()
initCoreByYear.groupby('FY').CORE_PROJECT_NUM.count().plot(kind='bar')
plt.ylim((0,6000))
ax.set_title('Number of new grants')
ax.set_ylabel('count')
# Note that 2001 is off the scale and should not be counted because this is the 
# the first year we have available data, even though some grants may have renewals
# but they nonetheless appear as new 

ax = fig.add_subplot(2,2,3)
# look at applications types 1 2 3 (new, competing renewal, and competing revision)
R01data.groupby('FY').APPLICATION_TYPE.apply(lambda x: sum((x==1)|(x==2)|(x==3))).plot(kind='bar')
ax.set_title('Number of type 1,2,3 grants (new, competing renewal, or revision)')
ax.set_ylabel('count')

ax = fig.add_subplot(2,2,4)
# number of non-competitive renewals (type 5), the most numerous application types 
R01data.groupby('FY').APPLICATION_TYPE.apply(lambda x: sum(x==5)).plot(kind='bar')
ax.set_title('Number of type 5 grants (non-competitive renewals)')
ax.set_ylabel('count')

if saveFigFlg:
	fig.set_size_inches(18.5,10.5)
	plt.savefig('R01_numGrantsByFY',dpi=100)


# Look at things by funding institute 
# ---------------------------------------------------------
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
# get rid of null values 
R01data2 = R01data[R01data.FUNDING_ICs.notnull()]
# add new column with shorterned institute abbr
R01data2['IC'] = R01data2.FUNDING_ICs.apply(lambda x: x.split(':')[0])
# now group by IC
R01dataICtotal = R01data2.groupby('IC').TOTAL_COST.sum().divide(1e9)
R01dataICtotal.sort(ascending=False)
R01dataICtotal.plot(kind='bar')
ax.set_title('Total Cost by Funding Institute (in billions)')
ax.set_ylabel('$ (in billions)')
if saveFigFlg:
	fig.set_size_inches(12,8)
	plt.savefig('R01_costByIC',dpi=100)

# Now take the top N funding institutes and look at how their funding changed over time
costICByFY = pd.DataFrame()
topN = 10
for inst in R01dataICtotal.index[0:topN]:
	costICByFY[inst] = R01data2[R01data2.IC == inst].groupby('FY').TOTAL_COST.sum().divide(1e6)
ttl = 'Total Cost for Top %d Funding Institute' % topN
ax = costICByFY.plot(colormap='jet',title=ttl)
ax.set_ylabel('$ (in millions)')

if saveFigFlg:
	fig.set_size_inches(12,8)
	plt.savefig('R01_costByICandFY',dpi=100)
