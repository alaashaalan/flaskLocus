from __future__ import division
from datetime import date, datetime, timedelta
import math
import db

def rssi_to_meter(rssi): #code works but will need some modification based what type of string we pass it
	RSSI_1m = -53.16667  #this value is experimentally measured
	distance = 10**((RSSI_1m - rssi)/20)
	return distance

# Process raw message and return as dictionary
def process_message(message):
	"""
	take a message string and parse it
	return: None
	"""
	message_values = message.split(',')
	print message_values
	if message_values[1] != "$GPRP":  #if this is not a valid message from the gateway, ignore
		print('ignoring this message')
		processed_message = {}
	else:
		# print message_values		
		processed_message = {'time_stamp': message_values[0],'report_type': message_values[1], 'tag_id': message_values[2], 'gateway_id': message_values[3], 'rssi': message_values[4], 'raw_packet_content': message_values[5]}
	return processed_message


def perdelta(start, end, delta):
	"""
	helper to generate time range
	"""
	curr = start
	while curr < end:
		yield curr
		curr += delta


def timestamp_matching(start_time, end_time, beacon, gateway_ids):
	# create a new table
	conn, c = db.connection();

	drop_statement = (
		"DROP TABLE IF EXISTS matched_timestamps;")
	c.execute(drop_statement)
	c.fetchall()

	create_table_statement = (
		"CREATE TABLE matched_timestamps (id INT NOT NULL AUTO_INCREMENT, time_stamp DATETIME(6), rssi1 FLOAT, rssi2 FLOAT, rssi3 FLOAT, PRIMARY KEY (id));"
		)
	c.execute(create_table_statement)
	c.fetchall()

	c.execute("SELECT * FROM raw_data;")
	results = c.fetchall()

	# iterate over all timestamps, look for rssis for the timestamp, add to the new table
	for timestamp in perdelta(start_time, end_time, timedelta(seconds=1)):
		rssi1 = db.find_avg_rssi(timestamp, timestamp, beacon, gateway_ids[0])
		rssi2 = db.find_avg_rssi(timestamp, timestamp, beacon, gateway_ids[1])
		rssi3 = db.find_avg_rssi(timestamp, timestamp, beacon, gateway_ids[2])

		insert_statement = "INSERT INTO matched_timestamps (time_stamp, rssi1, rssi2, rssi3) VALUES (%s, %s, %s, %s);"
		data = (str(timestamp), rssi1, rssi2, rssi3)

		c.execute(insert_statement, data)
		conn.commit()
	
	select_statement = ("SELECT * FROM matched_timestamps;")
	c.execute(select_statement)
	results = c.fetchall()
	conn.close()
	return results






# this is only executed if called explicitly. For debugging purposes only
if __name__ == "__main__":
	import db
	# prepare database
	locus_data = db.locus_data

	# sample messages
	messages = """$GPRP,5826D8AF76AB,D897B89C7B2F,-98,02011A07FF4C0010020B00
$GPRP,4129B7F0EF39,D897B89C7B2F,-76,02010613FF4C000C0E0013CCDE0B4ADD21CA00C43279D1
$GPRP,9801A7E1F444,D897B89C7B2F,-75,02010607FF4C0010020B00
yolo
$GPRP,542F70C06513,D897B89C7B2F,-83,02010607FF4C0010020B00
$GPRP,4129B7F0EF39,D897B89C7B2F,-80,02010613FF4C000C0E0013CCDE0B4ADD21CA00C43279D1
$GPRP,9801A7E1F444,D897B89C7B2F,-80,02010607FF4C0010020B00
$GPRP,4129B7F0EF39,D897B89C7B2F,-80,02010613FF4C000C0E0013CCDE0B4ADD21CA00C43279D1
$GPRP,5826D8AF76AB,D897B89C7B2F,-98,02011A07FF4C0010020B00
$GPRP,9801A7E1F444,D897B89C7B2F,-79,02010607FF4C0010020B00"""
	messages = messages.split('\n')

	# process messages
	for message in messages:
		processed_message = process_message(message)
		db.insert_raw_data(processed_message)

	print(len(locus_data))


