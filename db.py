import pprint
import MySQLdb
import config


# Returns credentials to connect to database
def connection():
	credentials = config.credentials()
	connection = MySQLdb.connect(host=credentials['host'],
		user=credentials['user'],
		passwd=credentials['passwd'],
		db=credentials['db'])

	cursor = connection.cursor();
	
	return connection, cursor

# Inserts newly collected data to table raw_data
def insert_raw_data(row):
	connection, cursor = connection();
	insert_statement = (
		"INSERT INTO raw_data (time_stamp, tag_id, gateway_id, rssi, raw_packet_content)"
		"VALUES (%s, %s, %s, %s, %s)"
		)
	data = (row['time_stamp'], row['tag_id'], row['gateway_id'], row['rssi'], row['raw_packet_content'])

	cursor.execute(insert_statement, data)

	connection.commit()
	connection.close()

# Finds specific beacons based on their id from raw_data table
def find_by_tag_id(table_name, fields, tag_id):
	connection, cursor = connection();
	query ="SELECT %s FROM %s WHERE tag_id = %s" %(fields, table_name, '%s')
	cursor.execute(query, [tag_id])
	records = cursor.fetchall()

	return records

# Finds all records between a specific time frame for a specific table (STRING INPUTS)
def find_by_datetime_range(table_name, fields, time_stamp_start, time_stamp_end):
	connection, cursor = connection();
	query = "SELECT %s FROM %s WHERE time_stamp >= %s AND time_stamp <= %s" % (fields, table_name, '%s', '%s')
	cursor.execute(query, [time_stamp_start, time_stamp_end])
	records = cursor.fetchall()

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