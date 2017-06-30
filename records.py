import numpy as np
import copy
from datetime import datetime, timedelta
import pandas as pd

from sklearn.neural_network import MLPClassifier
from sklearn import svm

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


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
		self.timestamp = record_tuple[0]  
		self.tag_id = record_tuple[1]
		self.gateway_id = record_tuple[2]
		self.rssi = record_tuple[3]
		self.raw_packet_content = record_tuple[4] 
		self.label = record_tuple[5]
		self.ntp = record_tuple[6]

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
		query = "SELECT * FROM raw_data WHERE tag_id = {} AND gateway_id = {} AND time_stamp >= {} AND time_stamp <= {}".format('%s', '%s', '%s', '%s')

		cursor.execute(query, [beacon, gateways, start, end])
		records = cursor.fetchall()
		database.close()
		for row in records:
			record = Record()
			# record.init_from_database(row)
			record.init_from_database(row)
			# print record

			self.append(record)


	def get_rssis(self):
		rssis = []
		for record in self:
			rssis.append(record.rssi)
		return rssis


	def average_rssi(self):

		return np.mean(self.get_rssis())


	def filter(self, window=60):
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
	def __init__(self, data_frame=None, gateway_list=None, classifier=None):
		self.data_frame = data_frame
		self.gateway_list = gateway_list
		self.classifier = classifier


	def init_from_database(self, beacon, gateways, start, end, filter_length=None):
		self.gateway_list = gateways

		all_data = {}
		for gateway in gateways:
			records = ListOfRecords()
			records.from_database(beacon, gateway, start, end)
			if filter_length is not None:
				records = records.filter(filter_length)
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
						# print "zero records for this second"
						continue
					matched_timestamps.ix[timestamp, gateway] = records.average_rssi()
					matched_timestamps.ix[timestamp, 'label'] = records[0].label

		return matched_timestamps

	def remove_nan(self):
		"""
		since gateways don't always start at the same time, 
		some secods don't have corresponding rssi and hence have NaN instead.
		Currenty machine learning lagorithms don't know how to handle NaN.
		As a temp fix, we're removing all records that have NaN in them. 
		"""
		dense_data = copy.deepcopy(self.data_frame)
		timestamps_to_remove = []
		for index, row in self.data_frame.iterrows():
			for gateway in self.gateway_list:

				if np.isnan(row[gateway]):
					# print 'removing row for ', index
					timestamps_to_remove.append(index)

		dense_data = self.data_frame.drop(timestamps_to_remove)
		print "removed {} rows containing NaN".format(len(timestamps_to_remove))
		return MatchedTimestamps(data_frame=dense_data, gateway_list=self.gateway_list)

	def convert_to_distance(self):
		raise NotImplementedError
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
		

	def train_NN(self):
		data = np.array(self.data_frame[self.gateway_list])
		labels = np.array(self.data_frame['label'])
		
		clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(10, 3), random_state=1)
		self.classifier = clf.fit(data, labels)
		return self.classifier		


	def train_SVM(self):
		data = np.array(self.data_frame[self.gateway_list])
		labels = np.array(self.data_frame['label'])

		clf = svm.SVC(probability=True)
		self.classifier = clf.fit(data, labels) 
		return self.classifier


	def accuracy_of_model(self):
		data = np.array(self.data_frame[self.gateway_list])
		labels = np.array(self.data_frame['label'])		
		return self.classifier.score(data, labels)


	def predict(self):
		data = np.array(self.data_frame[self.gateway_list])
		return self.classifier.predict(data)

	def predict_proba(self):
		data = np.array(self.data_frame[self.gateway_list])
		print self.classifier.predict_proba(data)


		
	def train_test_split(self, training_size=0.5, seed=None):
		gateway_list = self.gateway_list

		number_of_records = len(self.data_frame)
		split = int(number_of_records * training_size)

		np.random.seed(seed)
		indices = np.random.permutation(number_of_records)
		training_indeces, test_indeces = indices[:split], indices[split:]

		train_data_frame = self.data_frame.iloc[training_indeces]
		test_data_frame = self.data_frame.iloc[test_indeces]

		training = MatchedTimestamps(data_frame=train_data_frame,
			gateway_list=gateway_list)
		testing = MatchedTimestamps(data_frame=test_data_frame,
			gateway_list=gateway_list)

		return training, testing

	def plot(self):
		"""hacky plotting for four categories and 3 gateways"""

		ax = fig.add_subplot(111, projection='3d')
		gateway_list = self.gateway_list
		for label, c, m in zip(['1','2','3','4'], ['y', 'b', 'r', 'g'], ['x', '^', 'o', '*']):
			ts = self.data_frame.loc[self.data_frame['label'] == label]
			xs = ts[gateway_list[0]].values
			ys = ts[gateway_list[1]].values
			zs = ts[gateway_list[2]].values
			ax.scatter(xs, ys, zs, c=c, marker=m)

		ax.set_xlabel('X Label')
		ax.set_ylabel('Y Label')
		ax.set_zlabel('Z Label')		

	def _rename_label(self):
		matched_timestamps_merged =  copy.deepcopy(self)
		matched_timestamps_merged.data_frame = matched_timestamps_merged.data_frame.replace(['1-2', '1-3','1-4'],'1-1')
		matched_timestamps_merged.data_frame = matched_timestamps_merged.data_frame.replace(['2-2', '2-3','2-4'],'2-1')
		# matched_timestamps_merged.data_frame = matched_timestamps_merged.data_frame.replace(['3-2', '3-3','3-4'],'3-1')
		return matched_timestamps_merged

	def __repr__(self):

		return self.data_frame.__repr__()
		
if __name__ == "__main__":

	matched_timestamps =  MatchedTimestamps()

	# specify what beacon, gateway and timerange you're interested in
	# filter length=None means no filter
	# if you put filter=10 for example you will use moving average over 10 seconds

	# classification 2017-06-16 4 groups
	# matched_timestamps.init_from_database('0117C59B07A4', 
	# 	['CD2DA08685AD', 'FF9AE92EE4C9', 'D897B89C7B2F'], 
	# 	datetime(2017, 6, 16, 23, 34, 04, 0), datetime(2017, 6, 16, 23, 41, 51, 0), 
	# 	filter_length=20)

	# classification 5360 2017-06-27  3 aisles
	matched_timestamps.init_from_database('0CF3EE0B0BDD', 
		['CD2DA08685AD', 'FF9AE92EE4C9', 'D897B89C7B2F'], 
		datetime(2017, 6, 27, 1, 00, 18, 0), datetime(2017, 6, 27, 23, 59, 18, 0), 
		filter_length=10)

	# classification 2017-06-28 2 aisles
	# matched_timestamps.init_from_database('0117C59B07A4', 
	# 	['CD2DA08685AD', 'FF9AE92EE4C9', 'D897B89C7B2F'], 
	# 	datetime(2017, 6, 28, 19, 15, 04, 0), datetime(2017, 6, 28, 19, 35, 25, 0), 
	# 	filter_length=10)

	matched_timestamps = matched_timestamps.remove_nan()

	# matched_timestamps = matched_timestamps._rename_label() 
	
	# split the entire datasat into training and testing
	training, testing = matched_timestamps.train_test_split(training_size=0.70, seed=None)

	# # create a classfier using the trainging dataset
	svm = training.train_SVM()

	# # check accuracy of the testing dataset with training classifier
	accuracy = training.accuracy_of_model()
	print "accuracy of the training data is: " + str(accuracy)
	
	# # assigin the classifier to the testing dataset
	testing.classifier = svm
	
	# # check accuracy of the testing dataset with training classifier
	accuracy = testing.accuracy_of_model()
	print "accuracy of the testing data is: " + str(accuracy)
	
	# al's walk 2017-06-07
	# al_walk =  MatchedTimestamps()
	# al_walk.init_from_database('0117C59B07A4', 
	# 	['CD2DA08685AD', 'FF9AE92EE4C9', 'D897B89C7B2F'], 
	# 	datetime(2017, 6, 28, 19, 40, 21, 0), datetime(2017, 6, 28, 19, 41, 10, 0), 
	# 	filter_length=15)
	# al_walk = al_walk.remove_nan()
	# al_walk.classifier = svm
	# print list(al_walk.predict())
	# al_walk.predict_proba()

	# plot all data
	# fig = plt.figure()
	# matched_timestamps.plot()
	# plt.show()