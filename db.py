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
def insert_message(message):
	"""
	sample message: "$GPRP,0CF3EE0B0BDD,CD2DA08685AD,-67,0201061AFF4C0002152F234454CF6D4A0FADF2F4911BA9FFA600000001C5,1496863953"
	"""
	if not validate_message(message):
		return

	message = message.split(',')
	database, cursor = connection()
	label = get_app_label()
	time_stamp = datetime.fromtimestamp(int(message[5])).strftime('%Y-%m-%d %H:%M:%S')

	insert_statement = (
		"INSERT INTO raw_data (time_stamp, tag_id, gateway_id, rssi, raw_packet_content, ntp, label)"
		"VALUES (%s, %s, %s, %s, %s, %s, %s)"
		)

	data = (time_stamp, message[1], message[2], message[3], message[4], message[5], label)
	cursor.execute(insert_statement, data)
	database.commit()
	database.close()


def validate_message(message):
	message_values = message.split(',')
	if message_values[0] == "$GPRP":  #if this is not a valid message from the gateway, ignore
		return True
	else:
		return False


def insert_multiple_messages(messages):
	"""
	sample messages: 
	$GPRP,0CF3EE0B0BDD,CD2DA08685AD,-67,0201061AFF4C0002152F234454CF6D4A0FADF2F4911BA9FFA600000001C5,1496863953
	$GPRP,0CF3EE0B0BDD,CD2DA08685AD,-67,0201061AFF4C0002152F234454CF6D4A0FADF2F4911BA9FFA600000001C5,1496863953
	"""

	messages = messages.split('\n')
	for message in messages:
		insert_message(message)



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


def set_app_state(status, label):
	database, cursor = connection()

	if label == None:
		update_statement = 	"""
		   UPDATE app_state
		   SET status=%s
		"""
		cursor.execute(update_statement, [status])
	else:
		update_statement = 	"""
		   UPDATE app_state
		   SET status=%s, label=%s
		"""		
		cursor.execute(update_statement, (status, label))
	database.commit()
	database.close()


def get_app_state():
	database, cursor = connection()
	select_statement = 	"""
	   SELECT * from app_state
	"""
	cursor.execute(select_statement)
	state = cursor.fetchone()
	database.close()
	status = state[0]
	label = state[1]
	return status

def get_app_label():
	database, cursor = connection()
	select_statement = 	"""
	   SELECT * from app_state
	"""
	cursor.execute(select_statement)
	state = cursor.fetchone()
	database.close()
	status = state[0]
	label = state[1]
	return label

# this is only executed if called explicitly. For debugging purposes only
if __name__ == '__main__':
	pass
