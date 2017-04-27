from tinydb import TinyDB, where, Query
import pprint
import MySQLdb

#prepare database
#db = TinyDB('db.json')
#db.purge_table('_default')  # this is unnecessaryly risky
#locus_data = db.table('locus_data')

def connection():
	conn = MySQLdb.connect(host="localhost",
		user="root",
		passwd="12345",
		db="locus_development")

	c = conn.cursor();
	
	return conn, c


def insert(row):
	conn, c = connection();
	print row
	insert_statement = (
		"INSERT INTO raw_data (time_stamp, tag_id, gateway_id, rssi, raw_packet_content)"
		"VALUES (%s, %s, %s, %s, %s)"
		)
	data = (row['time_stamp'], row['tag_id'], row['gateway_id'], row['rssi'], row['raw_packet_content'])

	c.execute(insert_statement, data)

	conn.commit()
	conn.close()




# def insert(row):
# 	if len(row) == 0:
# 		pass
# 	else: 
# 		locus_data.insert(row)


# def find_tag_id(tag_id):
# 	Beacon = Query()
# 	beacons_with_tag = locus_data.search(Beacon.tag_id == tag_id)

# 	# for beacon in beacons_with_tag:
# 		# print(beacon['rssi'])

# 	return beacons_with_tag

# def convert_to_csv(list_of_records):
# 	csv_result = ""
# 	for row in list_of_records:
# 		try:
# 			csv_result += ','.join([row['time_stamp'], row['report_type'], row['tag_id'], row['gateway_id'], row['rssi'], row['raw_packet_content']]) + '\n'
# 		except KeyError, e:
# 			csv_result += ','.join(['', row['report_type'], row['tag_id'], row['gateway_id'], row['rssi'], row['raw_packet_content']]) + '\n'
 

# 	return csv_result


# def pretty_print(list_of_records):
# 	pp = pprint.PrettyPrinter(indent=4)
# 	for row in list_of_records:
# 		pp.pprint(row)






# # this is only executed if called explicitly. For debugging purposes only
# if __name__ == '__main__':
# 	convert_to_csv()
# 	pretty_print()

# 	print(convert_to_csv_list(find_tag_id('4129B7F0EF39'))) 