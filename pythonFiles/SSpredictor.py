"""
SSpredictor.py
"""
import os
import re
import urllib2
from zipfile import ZipFile
import csv
import time

import numpy as np
import pandas as pd
from pandas import DataFrame,Series
import random

from sklearn.preprocessing import LabelBinarizer
from sklearn.svm  import LinearSVC
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
#---------------------------------------------------------------------------------
# extract keywords for the last 4 years
# the training set is data from 2011-2013
# the test set is the data from the year 2014

def getXYdata(R01data):
    # function to extract keywords
    
    #replace all special emphasis study sections with NA
    R01data['STUDY_SECTION']=R01data['STUDY_SECTION'].apply(lambda x: np.nan if str.find(x,'Z') == 0 else x)


    R01data=R01data.dropna(subset=['STUDY_SECTION'])

    keyWords=pd.DataFrame(R01data['PROJECT_TERMS'])
    fundingIC=R01data[['STUDY_SECTION']]

    keyWords=keyWords.PROJECT_TERMS.apply(lambda x: x.lower())

    #split and remove delimiters from keywords and convert to list
    keyWords=keyWords.PROJECT_TERMS.apply(lambda x: x.lower()) #data type changes from dataframe to series
    keyWords=keyWords.apply(lambda x: re.split(r'[;,\s]\s*',x)) # regex applied to each element in the list of list
    keyWords=keyWords.tolist()

    # concat all the words for each grant to make the feature vector for each 
    # so now all the keywords for each grant form one corpus with no delimiters.
    # this makes generating the sparse matrix a lot easier
    spaceSt= " "
    grantKeyWords=list()
    for x in range(len(keyWords)):
        grantKeyWords.append(spaceSt.join(keyWords[x]))

    ICs,garbage,Ydata=np.unique(fundingIC,True,True)

    return(grantKeyWords,Ydata,keyWords)

#---------------------------------------------------------------------------------
#create the training set
years=range(2011,2014)

trainX=list()
trainY=list()
keyTrain=list()

for year in years: 
        path='/Users/anasuyadas/nobackup/Dropbox/Dropbox/data/RePORTER_PRJ_C_FY%d.csv' %year
        data=pd.read_csv(path,low_memory=False )
        R01data= data.ix[data.ACTIVITY=='R01',:].dropna(subset=['PROJECT_TERMS','STUDY_SECTION'])
        [grantKeyWords,Ydata,keyWords]= getXYdata(R01data)
        
        trainX.extend(grantKeyWords)
        trainY.extend(Ydata)
        keyTrain.extend(keyWords)

rows=len(trainX)
allIDX=range(rows)
random.shuffle(allIDX)

holdout=rows/10
testIdx=allIDX[0:holdout]
trainIdx=allIDX[holdout:]


xtrain=[trainX[i] for i in trainIdx]
xtest=[trainX[i] for i in testIdx]

ytrain=[trainY[i] for i in trainIdx]
ytest=[trainY[i] for i in testIdx]

#---------------------------------------------------------------------------------
#first flatten the list of lists, extract unique words to make a vocabulary set 
# the vocabulary is based only on the training set 
keyVocab = [y for x in keyTrain for y in x]
keyVocab =np.unique(keyVocab)
keyVocab=set(keyVocab)

# make a sparse matrix of the training Xdata
print "Extracting features from the training dataset using a sparse vectorizer"
t0 = time()
vec = CountVectorizer(vocabulary=keyVocab)
trainXsparse=vec.fit_transform(xtrain)

testXsparse=vec.fit_transform(xtest)

#---------------------------------------------------------------------------------

# #---------------------------------------------------------------------------------
year=2014
path='/Users/anasuyadas/nobackup/Dropbox/Dropbox/data/RePORTER_PRJ_C_FY%d.csv' %year
data=pd.read_csv(path,low_memory=False )
R01data= data.ix[data.ACTIVITY=='R01',:].dropna(subset=['PROJECT_TERMS','STUDY_SECTION'])
[grantTest,YTest,keyTest]= getXYdata(R01data)
#vectorize the test data using the same vocabulary as the training data
testSparse2014=vec.fit_transform(grantTest)

# #do the fitting
clf = MultinomialNB()
clf.fit(trainXsparse,ytrain)

clf.score(testXsparse,ytest) # 0.68632403081197124


clf = BernoulliNB()
clf.fit(trainXsparse,ytrain)
clf.score(testXsparse,ytest) # 0.67622174516984468


clf = LinearSVC()
clf.fit(trainXsparse,ytrain)
clf.score(testXsparse,ytest) # 0.94292208612198514



