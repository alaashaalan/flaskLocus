import numpy as np
import copy
from datetime import datetime, timedelta
import pandas as pd
from sklearn.neural_network import MLPClassifier

import db
import helper_functions
import optimization_trilateration
import locus


class Record:
	def __init__(self, timestamp=None, tag_id=None, gateway_id=None, rssi=None, raw_packet_content=None, label=None, ntp=None):
		self.timestamp = timestamp  
		self.tag_id = tag_id  
		self.gateway_id = gateway_id 
		self.rssi = rssi  
		self.raw_packet_content = raw_packet_content 
		self.label = label 
		self.ntp = ntp 

	def init_from_database(self, record_tuple):
		
		# print record_tuple
		# raise NotImplementedError
		self.timestamp = record_tuple[1]  
		self.tag_id = record_tuple[2]
		self.gateway_id = record_tuple[3]
		self.rssi = record_tuple[4]
		self.raw_packet_content = record_tuple[5] 
		self.label = record_tuple[6]
		self.ntp = record_tuple[7]

	def init_from_old_database(self, record_tuple):
		
		# print record_tuple
		# raise NotImplementedError
		self.timestamp = record_tuple[5]  
		self.tag_id = record_tuple[1]
		self.gateway_id = record_tuple[2]
		self.rssi = record_tuple[3]
		self.raw_packet_content = record_tuple[4] 
		self.label = record_tuple[6]
		self.ntp = record_tuple[5]

	def belongs_to_time_range(self, start, end):
		if self.timestamp >= start and self.timestamp <= end:
			return True
		else:
			return False

	def __repr__(self):

		return "\"{}, {}, {}, {}, {}\"".format(self.timestamp, self.gateway_id, self.tag_id, self.rssi, self.label)


class ListOfRecords(list):
	"""
	list_of_records - list of records for one beacon for one gateway
	"""
	def to_database():

		raise NotImplementedError


	def from_database(self, beacon, gateways, start, end):
		database, cursor = db.connection()
		# query = "SELECT * FROM test_data WHERE tag_id = {} AND gateway_id = {} AND time_stamp >= {} AND time_stamp <= {}".format('%s', '%s', '%s', '%s')
		query = "SELECT * FROM raw_data WHERE tag_id = {} AND gateway_id = {} AND ntp >= {} AND ntp <= {}".format('%s', '%s', '%s', '%s')

		cursor.execute(query, [beacon, gateways, start, end])
		records = cursor.fetchall()
		database.close()
		for row in records:
			record = Record()
			# record.init_from_database(row)
			record.init_from_old_database(row)

			self.append(record)


	def get_rssis(self):
		rssis = []
		for record in self:
			rssis.append(record.rssi)
		return rssis


	def average_rssi(self):

		return np.mean(self.get_rssis())


	def filter(self, window=10):
		rssis = []
		timestamps = []
		for record in self:
			rssis.append(record.rssi)
			timestamps.append(record.timestamp)

		# modes = ['full', 'same', 'valid']
		filtered_rssi = np.convolve(rssis, np.ones((window,))/window, mode='valid')

		copy_of_records = copy.deepcopy(self)
		for record, timestamp, filtered_rssi in zip(copy_of_records, timestamps, filtered_rssi):
			record.rssi = filtered_rssi
			record.timestamp = timestamp

		return copy_of_records


	def average_per_second(self):
		list_of_averaged_records = ListOfRecords()
		unique_timestamps = self.find_unique_timestamps()

		for timestamp in unique_timestamps:
			records_for_timestamps = ListOfRecords()
			for record in self:
				if record.belongs_to_time_range(timestamp, timestamp):
					records_for_timestamps.append(record)

			average_rssi = records_for_timestamps.average_rssi()
			tag_id = records_for_timestamps[0].tag_id
			gateway_id = records_for_timestamps[0].gateway_id
			label = records_for_timestamps[0].label
			new_record = Record(timestamp=timestamp, tag_id=tag_id, gateway_id=gateway_id, rssi=average_rssi, label=label)
			list_of_averaged_records.append(new_record)
		return list_of_averaged_records


	def find_unique_timestamps(self):
		timestamps = set([])
		for record in self:
			timestamps.add(record.timestamp)

		return sorted(timestamps)


	def find_records_for_time_range(self, start, end):
		records_for_timestamp = ListOfRecords()
		for record in self:
			if record.belongs_to_time_range(start, end):
				records_for_timestamp.append(record)

		return records_for_timestamp


class MatchedTimestamps:
	def __init__(self, data_frame=None, gateway_list=None):
		self.data_frame = data_frame
		self.gateway_list = gateway_list


	def init_from_database(self, beacon, gateways, start, end, filter=False):
		self.gateway_list = gateways

		all_data = {}
		for gateway in gateways:
			records = ListOfRecords()
			records.from_database(beacon, gateway, start, end)
			# records = records.filter()
			records = records.average_per_second()
			all_data[gateway] = records

		data_frame = self._match_by_time(all_data)
		self.data_frame = data_frame


	def _match_by_time(self, dict_of_lists_of_records):
		all_timestamps = set([])
		for list_of_records in dict_of_lists_of_records.values():
			all_timestamps = all_timestamps | set(list_of_records.find_unique_timestamps())
		all_timestamps = sorted(all_timestamps)

		columns = ['timestamp'] + self.gateway_list + ['label']
		matched_timestamps = pd.DataFrame(all_timestamps)
		matched_timestamps.columns = ['timestamps']
		matched_timestamps = matched_timestamps.set_index(['timestamps'])	

		for gateway in self.gateway_list:
			matched_timestamps[gateway] = np.nan

		for timestamp in all_timestamps:
				for gateway in self.gateway_list:
					records = dict_of_lists_of_records[gateway].find_records_for_time_range(timestamp,timestamp)
					if not len(records):
						print "zero records for this second"
					matched_timestamps.ix[timestamp, gateway] = records.average_rssi()
					matched_timestamps.ix[timestamp, 'label'] = records[0].label

		return matched_timestamps


	def convert_to_distance(self):
		distance_data_frame = copy.deepcopy(self.data_frame)
		for index, row in self.data_frame.iterrows():
			for gateway in self.gateway_list:
				distance_data_frame.ix[index][gateway] = helper_functions.rssi_to_meter(row[gateway])
		return distance_data_frame


	def trilaterate(self, location):
		raise NotImplementedError
		gateway_coordinates = []
		for gateway in location.list_of_gateways:
			gateway_coordinates.append(gateway.to_point().to_array())

		for index, row in self.data_frame.iterrows():
			distances = []
			for gateway in self.gateway_list:
				distances.append(row[gateway])		

			center = optimization_trilateration.trilaterate(gateway_coordinates, distances)
			print center
		

	def train(self):
		data = np.array(self.data_frame[self.gateway_list])
		labels = np.array(self.data_frame['label'])
		
		# some fake labels for now:
		labels = ([1] * 30 + [0] * 11)
		# labels = ([1] * len(labels))
		clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(5, 2), random_state=1)
		self.classifier = clf.fit(data, labels)
		return self.classifier.score(data, labels)
		

	def predict(self):
		data = np.array(self.data_frame[self.gateway_list])
		print self.classifier.predict_proba(data)



if __name__ == "__main__":
	timestamp1 = datetime.now()
	timestamp2 = timestamp1 + timedelta(seconds=1)

	record1 = Record(rssi=100, timestamp=timestamp1)
	record2 = Record(rssi=0, timestamp=timestamp1)
	record3 = Record(rssi=100, timestamp=timestamp2)
	record4 = Record(rssi=0, timestamp=timestamp2)

	new_lsit = ListOfRecords()
	new_lsit.append(record1)
	new_lsit.append(record2)
	new_lsit.append(record3)
	new_lsit.append(record4)

	print new_lsit.get_rssis()
	another_new_lsit = new_lsit.filter(window=2)
	print another_new_lsit.find_unique_timestamps()

	print another_new_lsit.average_per_second()


	list_of_records = ListOfRecords()
	list_of_records.from_database('A', 'A', datetime(2017, 6, 15, 23, 51, 18, 826376), datetime(2017, 6, 15, 23, 51, 18, 826376))
	# pandas_dataframe, all_data = matched_timestamps('A', ['A', 'B', 'C'], datetime(2017, 6, 15, 23, 51, 18, 826376), datetime(2017, 6, 15, 23, 51, 19, 826376))
	
	matched_timestamps =  MatchedTimestamps()
	matched_timestamps.init_from_database('0CF3EE0B0BDD', 
		['CD2DA08685AD', 'FF9AE92EE4C9', 'D897B89C7B2F'], 
		1496863900, 1496863940, filter=False)
	# dist_dataframe = matched_timestamps.convert_to_distance()
	# print dist_dataframe
	print matched_timestamps.train()
	matched_timestamps.predict()