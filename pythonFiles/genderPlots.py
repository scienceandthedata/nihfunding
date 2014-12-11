"""
genderPlots..py
"""

import pandas as pd
import numpy as np

import statsmodels.formula.api as sm
from sklearn.linear_model import LinearRegression
import scipy, scipy.stats

import matplotlib.pyplot as plt
from bokeh.plotting import *
from bokeh.charts import Bar

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------

def makeLine(grantType,outFile,plotTitle):
    data=pd.read_csv('/datascience/nihProject/rawData/%snumByGender.csv'%grantType,index_col=0)

    years = data['year'].unique()

    reset_output()
    output_file(outFile, title=plotTitle)

    clrs=['#6897bb','#6B6B6B','#ff7373']
    men=data['count'].ix[0].values
    unknown=data['count'].ix[1].values
    women=data['count'].ix[2].values



    # countData=dict(men=men,women=women, unknown=unknown)

    # bar= Bar(countData,years,filename="stacked_bar.html")
    # bar.title("Stacked bars").xlabel("years").ylabel("Percent").legend(True).stacked().show()

    figure(tools="pan,wheel_zoom,box_zoom,reset,previewsave")
    hold()
    rect(x=years, y=unknown, width=0.6, height=unknown, color=clrs[1],
        title="Pre-doctoral F31 grants by gender", y_range=[0, max(men+women+unknown)], plot_width=800,
        y_axis_label="number of grants",x_axis_label="years")
    rect(x=years, y=unknown + 10, width=0.6, height=10, color='white')

    rect(x=years, y=10+unknown + women/2, width=0.6, height=women, color=clrs[2])
    rect(x=years, y=10 + unknown + women, width=0.6, height=10, color='white')

    rect(x=years, y=10+unknown + women + men/2, width=0.6, height=men, color=clrs[0])
    grid().grid_line_color=None

    figure(tools="pan,wheel_zoom,box_zoom,reset,previewsave")
    hold()
    for i in range(0,3):
        line(years,data['percent'].ix[i],line_color=clrs[i],line_width=2,y_axis_label="% of total grants",x_axis_label="years")
        circle(years,data['percent'].ix[i],line_color=clrs[i], fill_color=clrs[i],size =10)

    grid().grid_line_color=None
    
    
    legend=True

    show()


