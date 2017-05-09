"""
This is explaratory analysis of collected data. Mostly just plotting. Incomplete
"""


import MySQLdb
import matplotlib 
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
# import pandas as pd 

database = MySQLdb.connect("localhost","user","","locus_development" )
cursor = database.cursor()
cursor.execute("SELECT * from raw_data")


beacons = ['0CF3EE0B0BDD', '0CF3EE0B08CA']
gateways = ['D897B89C7B2F','CD2DA08685AD','FF9AE92EE4C9']


for beacon in beacons:
	select_statement = (
		"SELECT rssi FROM  raw_data " 
		"WHERE time_stamp >= '2017-05-04 23:04:51' AND "
		"time_stamp <=  '2017-05-04 23:07:17' AND " 
		"tag_id = %s AND " 
		"gateway_id = %s")

	select_dates = (
		"SELECT time_stamp FROM  raw_data " 
		"WHERE time_stamp >= '2017-05-04 23:04:51' AND "
		"time_stamp <=  '2017-05-04 23:07:17' AND " 		
		"tag_id = %s AND " 
		"gateway_id = %s")

	data = (beacon, gateways[0])

	cursor.execute(select_statement, data)
	rssis = cursor.fetchall()

	cursor.execute(select_dates, data)
	dates = np.array(cursor.fetchall())
	dates = dates.flatten()
	# print dates

	dates = matplotlib.dates.date2num(dates)
	plt.plot_date(dates, rssis)
	plt.gcf().autofmt_xdate()

# plt.show()


cursor.execute("select * from raw_data")
data = cursor.fetchall()

data = np.array(data)
# df = pd.DataFrame(data)
# df.to_csv("file_path.csv")



for row in data:
	row[0] = str(row[0])



print type(data[0][0])
np.savetxt('test.out', data, delimiter=',', fmt='%s')