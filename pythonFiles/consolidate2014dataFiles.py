# import modules
import pandas as pd # import as pd conventional
from pandas import DataFrame, Series
import numpy as np # import as np conventional
import os
import matplotlib.pyplot as plt
import re

#------------------------------------------------------------------------------------------------

files = [f for f in os.listdir(dataPath) if os.path.isfile(f) and 'RePORTER_PRJ_C_FY2014' in f]
data = pd.read_csv(files.pop(0))

for file in files:
	newData = pd.read_csv(file)
	data = data.append(newData)

data.to_csv('RePORTER_PRJ_C_FY2014.csv')