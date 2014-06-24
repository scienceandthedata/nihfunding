
""" explore when NIH starts adding what columns
as soon as one value is not equal to NaN, we set year to start dataframe
there can still be missing values after that date """

#------------------------------------------------------------------------------------

# import modules
import pandas as pd # import as pd conventional
from pandas import DataFrame, Series
import numpy as np # import as np conventional
import os
import matplotlib.pyplot as plt
import re

#------------------------------------------------------------------------------------

files = [f for f in os.listdir(dataPath) if os.path.isfile(f) and 'RePORTER' in f]
startDates = {}
for file in files:
	data = pd.read_csv(file)
	headers = data.columns.values.tolist()
	year = re.search(r'\d\d\d\d', file).group()	
	for header in headers:
		entries = data[header].dropna()
		if not entries.any():
			print "No entries for " + header + " in " + year + "\n"
		elif not header in startDates:
			print "Entries for " + header + " starting in " + year + "\n"
			startDates[header] = year

StartDates = DataFrame(startDates.values(), index = startDates.keys(), columns = ['year'])
StartDates.to_csv('StartDatesOfRecording.csv')