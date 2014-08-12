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
import os
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

    #  make grouped names into a dictionary
    groupedNames=groupedNames.groupby(['name'][0])


    if saveFile:
        groupedNames.to_csv('names%donwards.csv'%numYears)

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
# read in data and create consolidated files and set some paths
workingPath=os.getcwd()

dataPath='/datascience/nihProject/rawData'
dataPath='/Users/anasuyadas/nobackup/Dropbox/Dropbox/data pirates shared folder/NIH-projectFiles/dataFiles'

figurePath='/datascience/nihProject/figures'

os.chdir(dataPath)

#data = pd.read_csv('/datascience/nihProject/rawData/NIHData.csv')


#create consolidated file
#data=loadNIHData(15,1)

#create consolidated name lookup file
#names= extractNamesDict(1980,1)

#R01data = data.ix[data.ACTIVITY=='R01',:]

#R01data.to_csv('datascience/nihProject/rawData/R01data.csv')

#---------------------------------------------------------------------------------

#R01data = pd.read_csv('/datascience/nihProject/rawData/R01data.csv')

years=range(2000,2015)
numGrantsGender=np.zeros([1,4])
costGrantsGender=np.zeros([4,1])

for year in years: 
    path='/Users/anasuyadas/nobackup/Dropbox/Dropbox/data pirates shared folder/NIH-projectFiles/dataFiles/RePORTER_PRJ_C_FY%d.csv' %year
    data=pd.read_csv(path,low_memory=False )
    R01data = data.ix[data.ACTIVITY=='R01',:]
    PIfirstNames=getPIfirstNames(R01data)

    print 'getting gender data for year: %d' %year 
    PIgender=getGenderIndex(PIfirstNames['first'])
    PIgender=PIgender.reset_index(drop=True)

    R01datanew=R01data.reset_index(drop=True)
    R01datanew=pd.concat([R01datanew,   PIgender],axis=1)

    print 'writing gender data for year: %d'  %year 
    R01datanew.to_csv('/datascience/nihProject/rawData/R01dataGender%d.csv'%year)


