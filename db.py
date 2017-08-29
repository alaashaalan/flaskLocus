from datetime import datetime, timedelta
import pprint
import MySQLdb
import config
import numpy as np
import helper_functions
import cPickle as pickle


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
	ntp_timestamp = int(message[5])
	time_stamp = datetime.fromtimestamp(ntp_timestamp).strftime('%Y-%m-%d %H:%M:%S')

	insert_statement = (
		"INSERT INTO raw_data (time_stamp, tag_id, gateway_id, rssi, raw_packet_content, ntp, label)"
		"VALUES (%s, %s, %s, %s, %s, %s, %s)"
		)

	data = (time_stamp, message[1], message[2], message[3], message[4], message[5], label)
	cursor.execute(insert_statement, data)
	database.commit()
	database.close()

def save_classifier(classifier, classifier_name):

	database, cursor = connection()
	classifier = pickle.dumps(classifier)

	insert_statement = (
		"INSERT INTO classifiers (classifier, classifier_name)"
		"VALUES (%s, %s)"
		)

	data = (classifier, classifier_name)
	cursor.execute(insert_statement,data)
	database.commit()
	database.close()

def load_classifier(classifier_name):

	database, cursor = connection()

	query = "SELECT classifier FROM classifiers WHERE classifier_name = {}".format('%s')
	cursor.execute(query, [classifier_name])
	classifier = cursor.fetchall()
	classifier = helper_functions.flatten_2d_struct(classifier)
	classifier = classifier[0]
	classifier = pickle.loads(classifier)
	database.close()
	return classifier

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
