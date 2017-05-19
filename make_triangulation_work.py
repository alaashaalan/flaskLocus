"""
This is explaratory analysis of collected data. Mostly just plotting. Incomplete
"""


import MySQLdb
import matplotlib 
from matplotlib.dates import date2num
import matplotlib.pyplot as plt
# from datetime import datetime
import numpy as np
# # import pandas as pd 

database = MySQLdb.connect("localhost","user","","locus_development" )
cursor = database.cursor()
# cursor.execute("SELECT * from raw_data")


beacons = ['0CF3EE0B0BDD', '0CF3EE0B08CA', '0117C59B07A4']
gateways = ['D897B89C7B2F','CD2DA08685AD','FF9AE92EE4C9']
labels = ['2m1b', '4m1b', '6m1b', '8m1b', '10m1b', '12m1b', '14m1b', '16m1b', '18m1b', '20m1b', '22m1b', '24m1b', '26m1b', '28m1b']
numeric_label = [2,4,6,8,10,12,14,16,18,20,22,24,26,28]
colors = ['r','b', 'y', 'k']

# csv = np.array([]).reshape(0,2)
all_rssis = []
all_dist = []

for gateway in [gateways[2]]:
	plt.figure()
	axes = plt.gca()
	axes.set_xlim([0,25])
	axes.set_ylim([-100,-60])
	for label_index, label in enumerate(labels):
		for ind, beacon in enumerate([beacons[2]]):
			rssi_select_statement = (
				"SELECT rssi FROM  raw_data " 
				"WHERE tag_id = %s AND "
				"gateway_id =  %s AND "  
				"label = %s")

			data = (beacon, gateway, label)

			cursor.execute(rssi_select_statement, data)
			rssis = np.array(cursor.fetchall())
			mean = np.mean(rssis)
			std = np.std(rssis)
			error_bar = std

			# filtered_rssis_idices = np.where((rssis < (mean + std))  & (rssis > (mean - std)))
			# filtered_rssis = rssis[filtered_rssis_idices]
			filtered_rssis = rssis
			dist = np.ones(filtered_rssis.shape) * numeric_label[label_index]

			# print(rssis.shape[0], filtered_rssis.shape[0], (rssis.shape[0] + filtered_rssis.shape[0]))

			plt.plot(dist, filtered_rssis)
			plt.errorbar(numeric_label[label_index], mean, error_bar, linestyle='None', marker='^')


			all_dist += dist.tolist()
			all_rssis += filtered_rssis.tolist()

			

			# timestamp_select_statement = (
			# 	"SELECT time_stamp FROM  raw_data " 
			# 	"WHERE tag_id = %s AND "
			# 	"gateway_id =  %s AND "  
			# 	"label = %s")

			# data = (beacon, gateway, label)

			# cursor.execute(timestamp_select_statement, data)
			# time_stamps = cursor.fetchall()	

			# # print time_stamps
			# time_stamps = np.array(time_stamps)
			# time_stamps = time_stamps.flatten()

			# dates = date2num(time_stamps)
			# plt.plot_date(dates, rssis, fmt=colors[ind])
			# plt.gcf().autofmt_xdate()		


csv = np.transpose(np.vstack([all_rssis, all_dist]))
print csv
np.savetxt('FF9AE92EE4C9_0CF3EE0B0BDD.csv', csv, delimiter=',', fmt='%s')
plt.show()
# 	cursor.execute(select_dates, data)
# 	dates = np.array(cursor.fetchall())
# 	dates = dates.flatten()
# 	# print dates

# 	dates = matplotlib.dates.date2num(dates)
# 	plt.plot_date(dates, rssis)
# 	plt.gcf().autofmt_xdate()




# cursor.execute("select * from raw_data")
# data = cursor.fetchall()

# data = np.array(data)
# df = pd.DataFrame(data)
# df.to_csv("file_path.csv")



# for row in data:
# 	row[0] = str(row[0])



# print type(data[0][0])
# np.savetxt('2017-05-09-park.csv', data, delimiter=',', fmt='%s')