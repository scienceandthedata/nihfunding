"""
ICpredictor.py
"""
from sklearn.preprocessing import LabelBinarizer
from sklearn.svm  import LinearSVC
import numpy as np
import pandas as pd
import csv
import random
import urllib
from sklearn.feature_extraction.text import CountVectorizer
import re
#---------------------------------------------------------------------------------
# extract keywords for the last 4 years
# the training set is data from 2011-2013
# the test set is the data from the year 2014

def getXYdata(R01data):
    # function to extract keywords
    
    R01data=R01data.dropna(subset=['PROJECT_TERMS'])

    keyWords=pd.DataFrame(R01data['PROJECT_TERMS'])
    fundinIC=R01data[['ADMINISTERING_IC']]

    #split and remove delimiters from keywords and convert to list
    keyWords=keyWords.PROJECT_TERMS.apply(lambda x: x.lower()) #data type changes from dataframe to series
    keyWords=keyWords.apply(lambda x: re.split(r'[;,\s]\s*',x)) # regex applied to each element in the list of list
    keyWords=keyWords.tolist()

    # concat all the words for each grant to make the feature vector for each 
    # so now all the keywords for each grant form one corpus with no delimiters.
    # this makes generating the sparse matrix a lot easier
    str= " "
    grantKeyWords=list()
    for x in range(len(keyWords)):
        grantKeyWords.append(str.join(keyWords[x]))

    ICs,garbage,Ydata=np.unique(fundinIC,True,True)

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
        R01data= data.ix[data.ACTIVITY=='R01',:]
        [grantKeyWords,Ydata,keyWords]= getXYdata(R01data)
        
        trainX.extend(grantKeyWords)
        trainY.extend(Ydata)
        keyTrain.extend(keyWords)

rows=size(trainX)
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
year=2014
path='/Users/anasuyadas/nobackup/Dropbox/Dropbox/data/RePORTER_PRJ_C_FY%d.csv' %year
data=pd.read_csv(path,low_memory=False )
R01data= data.ix[data.ACTIVITY=='R01',:]
[grantTest,YTest]= getXYdata(R01data)

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
#do the fitting
clf = MultinomialNB()
clf.fit(trainXsparse,ytrain)

clf.score(testXsparse,ytest) # 0.68632403081197124


from sklearn.naive_bayes import BernoulliNB
clf = BernoulliNB()
clf.fit(trainXsparse,ytrain)
clf.score(testXsparse,ytest) # 0.67622174516984468


clf = LinearSVC()
clf.fit(trainXsparse,ytrain)
clf.score(testXsparse,ytest) # 0.94292208612198514



