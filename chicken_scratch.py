#########################START SECTION count, average by champ_id############################
import pandas as pd
import numpy as np
matches = pd.read_csv("matches.csv")

#learning merging columns
 #df = pd.DataFrame(np.random.randn(10, 4), columns=['a', 'b', 'c', 'd'], index=rands_array(5, 10))
#Docs here suck. They're way generic for n dimensional space
#http://pandas.pydata.org/pandas-docs/stable/merging.html

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

leblanc = matchesGroupedDF[matchesGroupedDF.champ_id==7]
leblanc2 = leblanc.set_index('champ_id')
leblancGrouped = leblanc2.groupby(['count'])
leblancGrouped.mean()	
#########################END SECTION count, average by champ_id#############################


##################START PLOTLY#######################################################
import plotly.plotly as py
from plotly.graph_objs import *
#no idea why but mean is an array and count is a numpy array before you change mean to a numpy array.

data = Data([Histogram(x=kayleGrouped.mean().reset_index()['count'].values, y=   kayleGrouped.mean().reset_index()['mean'].values)])
plot_url = py.plot(data, filename='kayle-histogram')
##################START PLOTLY#######################################################

#I don't think plotly allows you to change themes on your own. Back to looking for visualization libraries.
#You can manually edit every plot though. That'll work


################################START HTML TABLE#####################################
#A way to make html tables from python
#Even if we don't do plots an html table is necessary
#If you use a library try to use one that supports tag attributes. So it can't be a generic one just for tables. This way we can programmatically apply styles like bootstrap.
#http://www.decalage.info/python/html only for python 2.7
#Games Played ->	#1		#2		#3		#4		#5		#6
#Champ1			 	wr		wr		wr		wr		wr		wr
#Champ2
#Try printing w/o modules since Python sucks https://docs.python.org/2/tutorial/inputoutput.html
#If you spit out json you can probably use this: http://d3js.org/

#HIGHLY UNTESTED
champs = pd.read_csv("champs.csv")
f = open("index.php", 'w')

f.write('<!Doctype html><html></head>\n<!-- Latest compiled and minified CSS -->\n<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css">\n<!-- Optional theme -->\n<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap-theme.min.css">\n<!-- Latest compiled and minified JavaScript -->\n<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js"></script></head><body><table class="table"><thead><tr><td>Champion</td><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td><td>6</td><td>7</td><td>8</td><td>9</td><td>10</td><td>11</td><td>12</td><tr><tbody>\n')

for i in range(0,len(champs.index)):
	#print(champs.iloc[i,1])#names
	champ = matchesGroupedDF[matchesGroupedDF.champ_id==champs.iloc[i,0]]
	champ2 = champ.set_index('champ_id')
	champGrouped = champ2.groupby(['count'])
	champDF = champGrouped.mean().reset_index()
	champWR = champDF['mean'].values
	champCount = champDF['count'].values
	#champPage = champs.iloc[i,1] + ".html"
	#skip more than 12 games played
	j = 0
	f.write('<tr><td>' + str(champs.iloc[i,1]) + '</td>')
	for i in range(0, 12):
		if (champCount[j] == i+1):
			if (j != len(champCount)-2):
				j = j + 1
			f.write('<td>' + str(champWR[j]) + '</td>')
		else:
			f.write('<td>' + 'N/A' + '</td>')

f.write('<tbody></table></body></html>')
f.close()
		
	

	
################################END HTML TABLE#####################################