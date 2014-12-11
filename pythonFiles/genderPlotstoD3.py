"""
genderPlots2.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mpld3

import statsmodels.formula.api as sm
from sklearn.linear_model import LinearRegression
import scipy, scipy.stats
# --------------------------------------------------------------------------------
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
# set grant-type and load in the data. This will later be done iteratively to visualize the data for all the different grant types
grantType='R01'
numGrants=pd.read_csv('/datascience/nihProject/rawData/%snumByGender2014.csv'%grantType,index_col=0)
costGrants=pd.read_csv('/datascience/nihProject/rawData/%scostByGender2014.csv'%grantType,index_col=0)

costGrants['sum']=np.divide(costGrants['sum'],10000)
years = numGrants['year'].unique()
    

paramsNumM=doLinearReg(years,numGrants['percent'].ix[0])
paramsNumF=doLinearReg(years,numGrants['percent'].ix[2])

fittedLineNumM=np.multiply(paramsNumM['x1'],years)+ paramsNumM['const']
fittedLineNumF=np.multiply(paramsNumF['x1'],years)+ paramsNumF['const']

ratio=np.divide(numGrants['count'].ix[0],numGrants['count'].ix[2])
paramsRatio= doLinearReg(years,ratio)

clrs=['#6897bb','#6B6B6B','#ff7373']
fig = plt.figure(figsize=(10,3))
fig, (ax1, ax2) = plt.subplots(1,2)
label=list()
labels=list()
for i in range(0,3): 
    fig1=ax1.scatter(years,costGrants['sum'].ix[i],s=30,color=clrs[i]) 
    labels= ['${0} billion'.format(j) for j in np.round(costGrants['sum'].ix[i],decimals=1)]
    label.append(labels)
    tooltip = mpld3.plugins.PointLabelTooltip(fig1, labels=labels)
    mpld3.plugins.connect(fig, tooltip)
#ax.set_title('Dollar value of RO1s by gender')
ax1.set_ylabel(' Amount in billions of Dollars')
ax1.set_xlabel('fiscal year')
ax1.set_xlim((2000,2016))
ax1.set_xticks(range(2000,2016,4))


label=list()
labels=list()
for i in range(0,3): 
    fig2=ax2.scatter(years,numGrants['percent'].ix[i],s=30,color=clrs[i]) 
    labels= ['% grants:{0}'.format(j) for j in np.round(numGrants['percent'].ix[i],decimals=1)]
    label.append(labels)
    tooltip = mpld3.plugins.PointLabelTooltip(fig2, labels=labels)
    mpld3.plugins.connect(fig, tooltip)
#ax.set_title('Dollar value of RO1s by gender')
ax2.set_ylabel(' RO1s awarded (%)')
ax2.set_xlabel('fiscal year')
ax2.set_xlim((2000,2016))
ax2.set_xticks(range(2000,2016,4))

mpld3.show()
# --------------------------------------------------------------------------------
clrs=['#1f77b4',' #ff7f0e','#2ca02c', '#d62728']
grantType=['F31','F32','K99','R01']
fig = plt.figure(figsize=(10,3))
fig, ax3 = plt.subplots(1,2)
label=list()
labels=list()
for i in range(0,3): 
    numGrants=pd.read_csv('/datascience/nihProject/rawData/%snumByGender2014.csv'%grantType,index_col=0)
    years = numGrants['year'].unique()

    ratio=np.true_divide(numGrants['percent'].ix[0],numGrants['percent'].ix[2])

    paramsRatio=doLinearReg(years,ratio)
    fittedRatio=np.multiply(paramsRatio['x1'],years)+ paramsRatio['const']
    yearEqual[i]=(1-paramsRatio['const'])/paramsRatio['x1']

    fig1=ax3.scatter(years,costGrants['sum'].ix[1],s=30,color=clrs[i]) 
    line1=ax3.plot(years,fittedRatio, color=clrs[], linestyle='-', linewidth=2)
    
    labels= ['Ratio M:W = {0}'.format(j) for j in np.round(costGrants['sum'].ix[i],decimals=1)]
    label.append(labels)
    tooltip = mpld3.plugins.PointLabelTooltip(fig1, labels=labels)
    mpld3.plugins.connect(fig, tooltip)
#ax.set_title('Dollar value of RO1s by gender')
ax3.set_ylabel(' Grants awarded to men:women')
ax3.set_xlabel('fiscal year')
ax3.set_xlim((2000,2016))
ax3.set_xticks(range(2000,2016,4))

