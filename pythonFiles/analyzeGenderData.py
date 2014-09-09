"""
analyzeGenderData.py
"""
import os
import re
import urllib2
from zipfile import ZipFile
import csv

import pandas as pd
import matplotlib.pyplot as plt
from pandas import DataFrame,Series
import numpy as np

import statsmodels.formula.api as sm
from sklearn.linear_model import LinearRegression
import scipy, scipy.stats
# --------------------------------------------------------------------------------
# This is the second file is part 2 of a series of script that slices the NIH data
# This file can do the following: 
#   - group NIH data by gender and return counts and costs by gender
#   - also returns costs by gender and by NIH institute
#   - also makes plots. The plots should ideally live in a different file - 
# --------------------------------------------------------------------------------
def doLinearReg(X,Y):
    # enter a data frame that has atleast one X and one Y column
    
    intercept = np.ones((len(X),1))
    #Y = data.iloc[:,2]
    X = np.column_stack((X,intercept))
    result = sm.OLS( Y, X ).fit()
    params=result.params
    return params
# --------------------------------------------------------------------------------

years=range(2000,2015)
numGrantsGender=pd.DataFrame()
costGrantsGender=pd.DataFrame()

#---------------------------------------------------------------------------------
for year in years: 
    R01data= pd.read_csv('/datascience/nihProject/rawData/R01dataGender%d.csv'%year,low_memory=False)

    bin=[-1.0001, -0.5, 0.5, 1.000001]

    groupsGender=R01data.groupby(pd.cut(R01data.gender,bin,labels=False))

    # get the number of grants and the average gender index by year
    numGrants=groupsGender['gender'].aggregate(['mean','std','count'])
    numGrants['year']=year 
    numGrants['percent']=100*numGrants['count'].divide(numGrants['count'].sum())
    numGrantsGender=numGrantsGender.append(numGrants)

    cost=groupsGender.TOTAL_COST.aggregate(['sum','mean','std'])
    cost=np.divide(cost,100000)
    cost['percent']=100*cost['sum'].divide(cost['sum'].sum())
    costGrantsGender=costGrantsGender.append(cost)

costGrantsGender.to_csv('/datascience/nihProject/rawData/R01costByGender.csv')
numGrantsGender.to_csv('/datascience/nihProject/rawData/R01costByGender.csv')

paramsNumM=doLinearReg(years,numGrantsGender['percent'].ix[0])
paramsNumF=doLinearReg(years,numGrantsGender['percent'].ix[2])

yearEqual=(50-paramsNumGrants['const'])/paramsNumGrants['x1']
#---------------------------------------------------------------------------------
# this is a table I grabbed of the net that shows % of tenure-track faculty by gender
#get params and values for the year
facultyGender=pd.read_csv('/datascience/nihProject/facultyByGender.csv')

paramsFacultyF=doLinearReg(facultyGender.iloc[:,0],facultyGender.iloc[:,1])
fittedLineFacultyF=np.multiply(paramsFacultyF['x1'],years)+ paramsFacultyF['const']

paramsFacultyM=doLinearReg(facultyGender.iloc[:,0],facultyGender.iloc[:,2])
fittedLineFacultyM=np.multiply(paramsFacultyM['x1'],years)+ paramsFacultyM['const']

fittedLineNumM=np.multiply(paramsNumM['x1'],years)+ paramsNumM['const']
fittedLineNumF=np.multiply(paramsNumF['x1'],years)+ paramsNumF['const']

normM=np.divide(fittedLineNumM,fittedLineFacultyM)
normF=np.divide(fittedLineNumF,fittedLineFacultyF)

#---------------------------------------------------------------------------------
#plot count of grants to each gender
fig = plt.figure(figsize=(18,7))
ax = fig.add_subplot(1,3,1)
plt.plot(years,numGrantsGender['count'].ix[0],'o',markersize=8,color='#00B2EE')#(70/255,130,180)) 
plt.plot(years,numGrantsGender['count'].ix[2],'o',markersize=8,color='#FF3030')
plt.plot(years,numGrantsGender['count'].ix[1],'o',markersize=8,color='0.7')
ax.set_title('Number of R01s by gender')
ax.set_ylabel(' Number of total RO1s awarded')
#ax.set_xlabel('fiscal year')
#plt.ylim((0,100))
plt.legend( ('male', 'female', 'unknown'),loc='upper right' )

#fig = plt.figure()
ax = fig.add_subplot(1,3,2)
plt.plot(years,numGrantsGender['percent'].ix[0],'o',markersize=8,color='#00B2EE') #male
plt.plot(years,numGrantsGender['percent'].ix[2],'o',markersize=8,color='#FF3030') # female
plt.plot(years,numGrantsGender['percent'].ix[1],'o',markersize=8,color='0.7') # unknown
plt.plot(years,fittedLineNumM,'-',color='#4682B4')#(70/255,130,180)) 
plt.plot(years,fittedLineNumF,'-',color='#CD5555')#(70/255,130,180)) 
ax.set_title('Percentage of R01s awarded by gender')
ax.set_ylabel(' RO1s awarded (%)')
ax.set_xlabel('fiscal year')
plt.ylim((0,100))
plt.legend( ('male', 'female', 'unknown'),loc='upper right' )

#fig = plt.figure()
ax = fig.add_subplot(1,3,3)
plt.plot(years,normM,'--',linewidth=2.0,color='#00B2EE')#(70/255,130,180)) 
plt.plot(years,normF,'--',linewidth=2.0,color='#FF3030')#(70/255,130,180)) 
ax.set_title('RO1s normalized to number of faculty by gender')
ax.set_ylabel(' Normalized RO1 funding rate')
#ax.set_xlabel('fiscal year')
plt.ylim((.5,1.5))
plt.legend( ('male', 'female', 'unknown'),loc='upper right' )

 fig.set_size_inches(18,7)
 plt.savefig('R01_numberGender',dpi=fig.dpi)
#---------------------------------------------------------------------------------
# plots for the dollar values
fig = plt.figure(figsize=(18,7))
ax = fig.add_subplot(1,2,1)
plt.plot(years,costGrantsGender['sum'].ix[0],'o',markersize=8,color='#00B2EE') 
plt.plot(years,costGrantsGender['sum'].ix[2],'o',markersize=8,color='#FF3030')
plt.plot(years,costGrantsGender['sum'].ix[1],'o',markersize=8,color='0.7')
ax.set_title('Dollar value of RO1s by gender')
ax.set_ylabel(' Amount ($)')
ax.set_xlabel('fiscal year')
#plt.ylim((0,100))
plt.legend( ('male', 'female', 'unknown'),loc='upper right' )

#fig = plt.figure()
ax = fig.add_subplot(1,2,2)
plt.plot(years,costGrantsGender['percent'].ix[0],'o',markersize=8,color='#00B2EE') 
plt.plot(years,costGrantsGender['percent'].ix[2],'o',markersize=8,color='#FF3030')
plt.plot(years,costGrantsGender['percent'].ix[1],'o',markersize=8,color='0.7')
ax.set_title('Percentage of total R01 money awarded by gender')
ax.set_ylabel(' % of total money')
ax.set_xlabel('fiscal year')
plt.ylim((0,100))
plt.legend( ('male', 'female', 'unknown'),loc='upper right' )

fig.set_size_inches(12,7)
plt.savefig('R01_grantCostsbyGender',dpi=300)