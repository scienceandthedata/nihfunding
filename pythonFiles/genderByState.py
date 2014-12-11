"""
genderByState.py
"""
import os
import re
import csv

import pandas as pd
import numpy as np
import os

# --------------------------------------------------------------------------------
# This file generates a CSV file of RO1 data by Gender for each state to be used 
# to make geo-coded maps in D3
# --------------------------------------------------------------------------------

year=2000

R01data= pd.read_csv('/datascience/nihProject/rawData/R01dataGender%d.csv'%year,low_memory=False)

bin=[-1.0001, -0.5, 0.5, 1.000001]

groupsGender=R01data.groupby(['ORG_STATE',pd.cut(R01data.gender,bin,labels=False)])

numGrants=groupsGender['gender'].aggregate(['count'])
numGrants=numGrants.reset_index()

states=numGrants['ORG_STATE'].unique()


numGrants=numGrants.set_index('ORG_STATE','level_1')

genderByState=pd.DataFrame()
countSum=pd.DataFrame()
ratio=pd.DataFrame()

for state in states:
    try:
        numGen=numGrants.ix[state]
        if len(numGen) >= 3 :
            Csum=numGrants.ix[state].sum()['count']        
            rat=  np.divide(numGen.ix[state].ix[2],numGen.ix[state].ix[0])['count']                 
        elif len(numGen) < 3 :
            Csum=numGen[1]
            rat=0            

        ratio=np.append(ratio,rat)
        countSum=np.append(countSum,Csum)
    except KeyError:
        Csum=0
        rat=0            
        ratio=np.append(ratio,rat)
        countSum=np.append(countSum,Csum)


ratio=ratio.reshape(len(ratio),1)
countSum=countSum.reshape(len(ratio),1)
states=states.reshape(len(ratio),1)

gendArray=np.hstack([states,ratio,countSum])

genderByState=genderByState.from_records(gendArray,columns=['state','ratio','countSum'])

genderByState.to_csv('/datascience/nihProject/rawData/R01bystate.csv')

# --------------------------------------------------------------------------------
# look up state names to match abbr
stateNames=pd.read_json('/Users/anasuyadas/nobackup/Dropbox/Dropbox/not_data/NIH-projectFiles/visualize/states.json')
stateNames=stateNames.set_index('abbreviation')
genderBystate=pd.read_csv('/datascience/nihProject/rawData/R01bystate.csv')

names =pd.DataFrame()
for state in genderBystate['state']:
    try:
        name=stateNames['name'].ix[state]
    except KeyError:
        name='none'
    names=np.append(names,name)

names=names.tolist()

genderBystate['names']= names

genderBystate.to_csv('/datascience/d3stuff/d3-figures/nihGender/R01StateName%d.csv'%year,
    columns=['state','ratio','countSum','names'],index = False )


           