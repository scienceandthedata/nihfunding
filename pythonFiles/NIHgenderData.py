"""
NIHgenderData.py
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
import random
# --------------------------------------------------------------------------------
# This is the first file of 2-part series of script that slices the NIH data
# This file can do the following: 
#   -create a consolidated name file for a given number of years.
#   - create a consolidated NIH or R01 data file for a given number of years
#   - alternatively append gender indexes to the above and write it out
# --------------------------------------------------------------------------------
def extractNamesDict(numYears,saveFile):
    # make a consolidated name file of a given number of years based on census data
    # first name, gender, num repeats
    # year from which files should be read
    namePath='/datascience/nihProject/genderPredictor/names'

    years=range(numYears,2010)

    names=pd.DataFrame()
    

    for year in years: 
        path='/datascience/nihProject/genderPredictor/names/yob%d.txt' %year
        frame=pd.read_csv(path)
        frame['year']=year
        frame.columns=['name','gender','reps','year']
        names=names.append(frame)

    # group names and add counts of names across years
    names.name=[name.lower() for name in names.name]
    aggrNames=names.groupby(['name','gender'])
    groupedNames= aggrNames.aggregate(np.sum)

    #  
    
    #groupedNames=groupedNames.groupby(['name'][0])


    if saveFile:
        groupedNames.to_csv('/datascience/nihProject/rawData/names%donwards.csv'%numYears)

    return names
# --------------------------------------------------------------------------------
def getGenderIndex(PIfirstNames):

    groupedNames=pd.read_csv('/datascience/nihProject/rawData/names1980onwards.csv')
    groupedNames.name[groupedNames.name.isnull()]='noName'
    groupedNames.name=[name.lower() for name in groupedNames.name]
    groupedNames=groupedNames.set_index('name')

    genderIndex=pd.DataFrame()
    

    for name in PIfirstNames:
        try:
            repsByGender=groupedNames.ix[name]
            if repsByGender.shape[0] ==3: # if there is a match corresponding to a single gender find out if male or female
                if 'M' in repsByGender['gender']: ind= -1 # check for up dict keys, 
                elif 'F' in repsByGender['gender']: ind=1
                genderIndex=np.append(genderIndex,ind)
            
            elif repsByGender.shape[0] == 2 : # if match for both gender generate gender index
                # this index estimates how much the gender of a particular name is contaminated by the other gender. 
                # the sign of the gender index is also automatically determined by the more common gender
                ind=(repsByGender.reps[0]-repsByGender.reps[1])/(repsByGender.reps[0]+repsByGender.reps[1])
                genderIndex=np.append(genderIndex,ind)

        except KeyError:
            genderIndex=np.append(genderIndex,np.nan)
        
        
        
    genderIndex.reshape(-1,1)
    PIgender=pd.DataFrame({'firstName':PIfirstNames,'gender':genderIndex})
    # genderIndex=pd.DataFrame.genderIndex()
    # pd.concat(PIfirstNames,genderIndex)

    return PIgender
# --------------------------------------------------------------------------------
def loadNIHData(nrFiles,saveFile):
# get NIH data
    
    files = [f for f in os.listdir(dataPath) if os.path.isfile(f) and year in f and '.csv' in f ] 

    if isinstance(nrFiles,str):
        pass
    elif nrFiles>len(files):
        print 'Limit # of files to load to less than:' + str(len(files))+'\n'
        return
    else:
        files=files[0:nrFiles]

    #print 'Loading data:' +files +'\n'
    data=pd.read_csv(files.pop(0),low_memory=False)
    #data = data.ix[data.ACTIVITY=='R01',:]



    for file in files:
        print 'Loading data: ' + file + '\n'
        newData=pd.read_csv(file,low_memory=False )
        data=data.append(newData)

    if saveFile:
        data.to_csv('/datascience/nihProject/rawData/NIHData.csv')

    return data
#---------------------------------------------------------------------------------
def getPIfirstNames(data):
#get PI names
    # take in yearwise NIH data and return PIfirst names


    dfPIs=data.PI_NAMEs.dropna()
    dfPIs = dfPIs.apply(lambda x: x.lower())
    dfPIs = dfPIs.apply(lambda x: x.split(';')[0])
    #split first and last names
    PInames= pd.DataFrame(dfPIs.str.split(', ',1).tolist(),columns=['last','first'])

    #split first and middle names
    mask=PInames['first'].isnull()
    PInames['first'][mask]='noName'

    PIfirstNames=pd.DataFrame(PInames['first'].str.split(' ',1).tolist(),columns=['first','middle'])

    return PIfirstNames
#---------------------------------------------------------------------------------
# test accuracy on yob2010 data
path='/datascience/nihProject/genderPredictor/names/yob%d.txt' %2010
names=pd.read_csv(path,header=None)
names[0]=names[0].apply(lambda x: x.lower())
names=names.drop_duplicates(cols=0,take_last=True)

# generate a random index
rows=len(names)
allIDX=range(rows)
random.shuffle(allIDX)

#randomly select half the names. This is in order to not double the error rate of the index.
randIdx=allIDX[0:rows/2]
randNames=names.ix[randIdx]

#replace the M, F strings with 1 or 2 so we can compare with the gender index
mapping={'F':2,'M':1}
randNames=randNames.replace({1:mapping}).dropna()
randNames=randNames.drop_duplicates(cols=0,take_last=True)


# get the gender index for all the names on the list
gender2010=getGenderIndex(randNames[0])

# use list comprehension to assign a gender  to each name if it is above or below a certain threshold
femStr=[2 if x>=0.5 else 0 for x in gender2010['gender']]
maleStr=[1 if x<=-0.5 else 0 for x in gender2010['gender']]
genderStr=np.add(femStr,maleStr)
numReturned=np.sum(genderStr!=0) # count the number of names for which a gender was assigned with high probability

correct=np.sum(genderStr==randNames[1])
propCorrect=np.true_divide(correct,numReturned)


    
# --------------------------------------------------------------------------------
# read in data and set some paths
workingPath=os.getcwd()

dataPath='/datascience/nihProject/rawData'
dataPath='/Users/anasuyadas/nobackup/Dropbox/Dropbox/data'

figurePath='/datascience/nihProject/figures'

os.chdir(dataPath)

#---------------------------------------------------------------------------------
years=range(2007,2015)
#K99's were introduced only in 2006
numGrantsGender=np.zeros([1,4])
costGrantsGender=np.zeros([4,1])
gender=pd.DataFrame()

for year in years: 
        path='/Users/anasuyadas/nobackup/Dropbox/Dropbox/data/RePORTER_PRJ_C_FY%d.csv' %year
        data=pd.read_csv(path,low_memory=False )
        R01data = data.ix[data.ACTIVITY=='K99',:]
        PIfirstNames=getPIfirstNames(R01data)

    print 'getting gender data for year: %d' %year 
    PIgender=getGenderIndex(PIfirstNames['first'])
    PIgender=PIgender.reset_index(drop=True)

    R01datanew=R01data.reset_index(drop=True)
    R01datanew=pd.concat([R01datanew,   PIgender],axis=1)

    print 'writing gender data for year: %d'  %year 
    R01datanew.to_csv('/datascience/nihProject/rawData/K99dataGender%d.csv'%year)


