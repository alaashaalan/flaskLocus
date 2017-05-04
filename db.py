from datetime import datetime, timedelta
import pprint
import MySQLdb
import config
import numpy as np


# Returns credentials to connect to database
def connection():
	credentials = config.credentials()
	database = MySQLdb.connect(host=credentials['host'],
		user=credentials['user'],
		passwd=credentials['passwd'],
		db=credentials['db'])

	cursor = database.cursor()
	
	return database, cursor

# Inserts newly collected data to table raw_data
def insert_raw_data(row):
	database, cursor = connection()
	insert_statement = (
		"INSERT INTO raw_data (time_stamp, tag_id, gateway_id, rssi, raw_packet_content)"
		"VALUES (%s, %s, %s, %s, %s)"
		)
	data = (row['time_stamp'], row['tag_id'], row['gateway_id'], row['rssi'], row['raw_packet_content'])

	cursor.execute(insert_statement, data)

	database.commit()
	database.close()


def find_avg_rssi(start_time, end_time, beacon, gateway):
	"""
	time in the following format: '2017-05-01 17:30:20'
	TODO: should we pass connection and cursor as arguments instead of openning every time?
	"""
	database, cursor = connection()
	select_statement = (
		"SELECT rssi FROM  raw_data " 
		"WHERE time_stamp >= %s AND "
		"time_stamp <= %s AND " 
		"tag_id = %s AND " 
		"gateway_id = %s")
	data = (start_time, end_time, beacon, gateway)
	cursor.execute(select_statement, data)
	rssis = cursor.fetchall()
	if len(rssis) == 0:
		avg_rssi = 0
	else:
		avg_rssi = np.average(rssis)
	database.close()
	return avg_rssi


# Finds specific beacons based on their id from raw_data table
'''
TODO: SQL Function input sanitization
'''
def find_by_tag_id(table_name, fields, tag_id):
	database, cursor = connection()
	query ="SELECT {} FROM {} WHERE tag_id = {}".format(fields, table_name, '%s')
	cursor.execute(query, [tag_id])
	records = cursor.fetchall()
	database.close()

	return records

# Finds all records between a specific time frame for a specific table (STRING INPUTS)
def find_by_datetime_range(table_name, fields, time_stamp_start, time_stamp_end):
	database, cursor = connection()
	query = "SELECT {} FROM {} WHERE time_stamp >= {} AND time_stamp <= {}".format(fields, table_name, '%s', '%s')
	cursor.execute(query, [time_stamp_start, time_stamp_end])
	records = cursor.fetchall()
	database.close()

	return records


# Needs to be updated to SQL
def convert_to_csv(list_of_records):
 	csv_result = ""
 	for row in list_of_records:
 		try:
 			csv_result += ','.join([row['time_stamp'], row['report_type'], row['tag_id'], row['gateway_id'], row['rssi'], row['raw_packet_content']]) + '\n'
 		except KeyError, e:
 			csv_result += ','.join(['', row['report_type'], row['tag_id'], row['gateway_id'], row['rssi'], row['raw_packet_content']]) + '\n'
 

 	return csv_result


# this is only executed if called explicitly. For debugging purposes only
if __name__ == '__main__':
	pass
