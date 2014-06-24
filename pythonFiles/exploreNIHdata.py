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

def barGraph(xvals,yvals,width,xTick,xLabel,yLabel,bottomAdjust,saveFigure):
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
	files = [f for f in os.listdir(dataPath) if os.path.isfile(f) and 'RePORTER' in f]
	
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

dJson = []
states = sorted(list(data.ORG_STATE.value_counts().index))
values = data.ORG_STATE.value_counts()
meanIncome = data['TOTAL_COST'].groupby(data.ORG_STATE).mean()

for state in states:
	dict1 = {}
	dict1['state'] = state
	dict2 = {}
	dict2['count'] = values[state]
	dict2['logCount'] = math.log(values[state])
	dict1['counts'] = dict2
	dict3 = {}
	dict3['meanIncome'] = meanIncome[state]
	dict3['logMeanIncome'] = math.log(meanIncome[state])
	dict1['money'] = dict3
	dJson.append(dict1)

dJson2 = {}
dJson2['data'] = dJson

with open("nih_states.json", "w") as outfile:
    json.dump(dJson2, outfile, sort_keys=True, indent=2)

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


