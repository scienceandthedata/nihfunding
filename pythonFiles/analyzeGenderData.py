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
import os

years=range(2000,2015)
numGrantsGender=np.zeros([1,4])
costGrantsGender=np.zeros([4,1])
gender=pd.DataFrame()

#---------------------------------------------------------------------------------
for year in years: 
    R01data= pd.read_csv('/datascience/nihProject/rawData/R01dataGender%d.csv'%year,low_memory=False)


    # numGrants=np.histogram(R01data.gender,bins=4,range=(-1,1),density=False)
    # numGrantsGender=np.vstack([numGrantsGender,numGrants[0]])

    bin=[-0.5, 0.0, 0.5, 1]

    groupsGender=R01data.groupby(np.digitize(R01data.gender,bin))
    cost=groupsGender.TOTAL_COST.aggregate(np.sum)
    cost=np.divide(cost,1000000)
    costGrantsGender=np.vstack([costGrantsGender,cost])
    
    meanCost=groupsGender.TOTAL_COST.aggregate(np.mean)
    stdCost=groupsGender.TOTAL_COST.aggregate(np.std)
    meanCost=np.divide(meanCost,1000000)
    stdCost=np.divide(stdCost,1000000)
    meanGrantsGender=np.vstack([meanGrantsGender,meanCost])
    stdGrantsGender=np.vstack([stdGrantsGender,stdCost])

costGrantsGender=np.reshape(costGrantsGender,(-1,4))
costGrantsGender=costGrantsGender[~np.isnan(costGrantsGender)]
costGrantsGender=np.reshape(costGrantsGender,(-1,4))


# numGrantsGender=numGrantsGender*100/numGrantsGender.sum(axis=1)[:,None]
# numGrantsGender=numGrantsGender[~np.isnan(numGrantsGender)]
# numGrantsGender=np.reshape(numGrantsGender,(-1,4))



# #---------------------------------------------------------------------------------
# plot count of grants to each gender

# fig = plt.figure()
# ax = fig.add_subplot(1,1,1)
# plt.plot(years,numGrantsGender[:,0],'-o',markersize=10,color='b') 
# plt.plot(years,numGrantsGender[:,3],'-o',markersize=10,color='r')
# plt.plot(years,numGrantsGender[:,1:2].sum(axis=1),'-o',markersize=10,color='k')
# ax.set_title('Number of R01s by gender')
# ax.set_ylabel('% of total RO1s awarded')
# ax.set_xlabel('fiscal year')
# plt.ylim((0,100))
# plt.legend( ('male', 'female', 'unknown'),loc='upper right' )


fig.set_size_inches(18.5,10.5)
plt.savefig('R01_grantCostsbyGender',dpi=100)

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
plt.plot(years,costGrantsGender[:,0],'-o',markersize=10,color='b') 
plt.plot(years,costGrantsGender[:,3],'-o',markersize=10,color='r')
plt.plot(years,costGrantsGender[:,1:2].sum(axis=1),'-o',markersize=10,color='k')
ax.set_title('Number of R01s by gender')
ax.set_ylabel('% of total RO1s awarded')
ax.set_xlabel('fiscal year')
plt.ylim((0,100))
plt.legend( ('male', 'female', 'unknown'),loc='upper right' )


fig.set_size_inches(18.5,10.5)
plt.savefig('R01_grantCostsbyGender',dpi=100)