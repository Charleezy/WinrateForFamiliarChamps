#########################START SECTION count, average by champ_id############################
import pandas as pd
import numpy as np
matches = pd.read_csv("matches.csv")

#learning merging columns
 df = pd.DataFrame(np.random.randn(10, 4), columns=['a', 'b', 'c', 'd'], index=rands_array(5, 10))
#Docs here suck. They're way generic for n dimensional space
http://pandas.pydata.org/pandas-docs/stable/merging.html

#so pandas doesn't do cbind as easily.
#You can cbind here but you're left with useless rows.

#gets all the games
matchesGrouped = matches.groupby(['summ_id','champ_id'])
#gets count and mean
matchesGrouped2 = matchesGrouped.agg(["count", "mean"])
#This is a multilevel index so drop a level
matchesGrouped2.index = matchesGrouped2.index.droplevel(0)
#converts back to dframe
#TODO: consider using set_index
#very consisten naming convention for methods. Sometimes use underscore. Sometimes no use. Exciting to never know!
matchesGroupedDF = matchesGrouped2.reset_index()
#I ended up with a bad dataframe with things on multiple levels
#Still not right
#removing first level to only have count and mean level. reset_index doesn't turn it back into a proper df
matchesGroupedDF.columns = matchesGroupedDF.columns.levels[1]
#resetting column names as index was set to champ_id by default (first column) probably by rest_index
matchesGroupedDF.columns = ['champ_id','count','mean']
#remove summoner_id no longer useful. Get index as champ_id
#matchesGroupedDF = matchesGroupedDF.set_index('champ_id')
#now we're at 'champ_id','count','mean' which is great
#########################END SECTION count, average by champ_id#############################



#########################START SECTION for each champion loop############################# 
champs = pd.read_csv("champs.csv")

#Because python's amazing at data manipulation, it's dataframes don't need a nrows method.
#They just use len(champs.index) ... ?_? wadafa?
for i in range(0,len(champs.index)):
	print(champs.iloc[i,1])#names
#########################END SECTION count, average by champ_id#############################
	
	
	
#########################START SECTION for each champion loop############################# 
#group by again, this time with count as index for champion x, and avg(avg) as column

kayle = matchesGroupedDF[matchesGroupedDF.champ_id==7]
kayle2 = kayle.set_index('champ_id')
kayleGrouped = kayle2.groupby(['count'])
kayleGrouped.mean()	
#########################END SECTION count, average by champ_id#############################


##################START PLOTLY#######################################################
import plotly.plotly as py
from plotly.graph_objs import *
#no idea why but mean is an array and count is a numpy array before you change mean to a numpy array.

data = Data([Histogram(x=kayleGrouped.mean().reset_index()['count'].values, y=   kayleGrouped.mean().reset_index()['mean'].values)])
plot_url = py.plot(data, filename='kayle-histogram')
##################START PLOTLY#######################################################

#I don't think plotly allows you to change themes on your own. Back to looking for visualization libraries. We did a lot today though :)