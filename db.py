from datetime import datetime, timedelta
import pprint
import MySQLdb
import config
import numpy as np


# Returns credentials to connect to database
def connection():
	credentials = config.credentials()
	conn = MySQLdb.connect(host=credentials['host'],
		user=credentials['user'],
		passwd=credentials['passwd'],
		db=credentials['db'])

	c = conn.cursor();
	
	return conn, c

# Inserts data to table raw_data
def insert_raw_data(row):
	conn, c = connection();
	insert_statement = (
		"INSERT INTO raw_data (time_stamp, tag_id, gateway_id, rssi, raw_packet_content)"
		"VALUES (%s, %s, %s, %s, %s)"
		)
	data = (row['time_stamp'], row['tag_id'], row['gateway_id'], row['rssi'], row['raw_packet_content'])

	c.execute(insert_statement, data)

	conn.commit()
	conn.close()


def find_avg_rssi(start_time, end_time, beacon, gateway):
	"""
	time in the following format: '2017-05-01 17:30:20'
	TODO: datetime is currently returned as 'None'. Need to fix
	TODO: should we pass connection and cursor as arguments instead of openning every time?
	"""
	conn, c = connection();
	select_statement = (
		"SELECT rssi FROM  raw_data " 
		"WHERE time_stamp >= %s AND "
		"time_stamp <= %s AND " 
		"tag_id = %s AND " 
		"gateway_id = %s")
	data = (start_time, end_time, beacon, gateway)
	c.execute(select_statement, data)
	rssis = c.fetchall()
	if len(rssis) == 0:
		avg_rssi = 0
	else:
		avg_rssi = np.average(rssis)
	conn.close()
	return avg_rssi

# Needs to be updated to SQL
def find_tag_id(tag_id):
	Beacon = Query()
	beacons_with_tag = locus_data.search(Beacon.tag_id == tag_id)

    # for beacon in beacons_with_tag:

	return beacons_with_tag

# Needs to be updated to SQL
def convert_to_csv(list_of_records):
 	csv_result = ""
 	for row in list_of_records:
 		try:
 			csv_result += ','.join([row['time_stamp'], row['report_type'], row['tag_id'], row['gateway_id'], row['rssi'], row['raw_packet_content']]) + '\n'
 		except KeyError, e:
 			csv_result += ','.join(['', row['report_type'], row['tag_id'], row['gateway_id'], row['rssi'], row['raw_packet_content']]) + '\n'
 

 	return csv_result

# Not sure if this works
def pretty_print(list_of_records):
 	pp = pprint.PrettyPrinter(indent=4)
 	for row in list_of_records:
 		pp.pprint(row)


# this is only executed if called explicitly. For debugging purposes only
if __name__ == '__main__':
 	convert_to_csv()
 	pretty_print()

 	print(convert_to_csv_list(find_tag_id('4129B7F0EF39'))) 