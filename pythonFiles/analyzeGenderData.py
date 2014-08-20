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

# --------------------------------------------------------------------------------
# This is the first file is part 2 of a series of script that slices the NIH data
# This file can do the following: 
#   - group NIH data by gender and return counts and costs by gender
#   - also returns costs by gender and by NIH institute
#   - also makes plots. The plots should ideally live in a different file - 
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


    


# #---------------------------------------------------------------------------------
#plot count of grants to each gender

fig = plt.figure()
ax = fig.add_subplot(2,2,1)
plt.plot(years,numGrantsGender['count'].ix[0],'o',markersize=10,color='b') 
plt.plot(years,numGrantsGender['count'].ix[2],'o',markersize=10,color='r')
plt.plot(years,numGrantsGender['count'].ix[1],'o',markersize=10,color='k')
ax.set_title('Number of R01s by gender')
ax.set_ylabel(' Number of total RO1s awarded')
ax.set_xlabel('fiscal year')
#plt.ylim((0,100))
plt.legend( ('male', 'female', 'unknown'),loc='upper right' )

#fig = plt.figure()
ax = fig.add_subplot(2,2,2)
plt.plot(years,numGrantsGender['percent'].ix[0],'o',markersize=10,color='b') 
plt.plot(years,numGrantsGender['percent'].ix[2],'o',markersize=10,color='r')
plt.plot(years,numGrantsGender['percent'].ix[1],'o',markersize=10,color='k')
ax.set_title('Number of R01s by gender')
ax.set_ylabel(' Number of total RO1s awarded')
ax.set_xlabel('fiscal year')
plt.ylim((0,100))
plt.legend( ('male', 'female', 'unknown'),loc='upper right' )

fig.set_size_inches(14,9)
plt.savefig('R01_grantCostsbyGender',dpi=100)

#fig = plt.figure()
ax = fig.add_subplot(2,2,3)
plt.plot(years,costGrantsGender['sum'].ix[0],'o',markersize=10,color='b') 
plt.plot(years,costGrantsGender['sum'].ix[2],'o',markersize=10,color='r')
plt.plot(years,costGrantsGender['sum'].ix[1],'o',markersize=10,color='k')
ax.set_title('Dollar value of RO1s by gender')
ax.set_ylabel(' Amount ($)')
ax.set_xlabel('fiscal year')
#plt.ylim((0,100))
plt.legend( ('male', 'female', 'unknown'),loc='upper right' )

#fig = plt.figure()
ax = fig.add_subplot(2,2,4)
plt.plot(years,costGrantsGender['percent'].ix[0],'o',markersize=10,color='b') 
plt.plot(years,costGrantsGender['percent'].ix[2],'o',markersize=10,color='r')
plt.plot(years,costGrantsGender['percent'].ix[1],'o',markersize=10,color='k')
ax.set_title('Dollar value of RO1s by gender')
ax.set_ylabel(' Percentage of total (%)')
ax.set_xlabel('fiscal year')
plt.ylim((0,100))
plt.legend( ('male', 'female', 'unknown'),loc='upper right' )