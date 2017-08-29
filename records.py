import numpy as np
import copy
from datetime import datetime, timedelta
import pandas as pd

from sklearn.neural_network import MLPClassifier
from sklearn import svm
from sklearn import preprocessing
from sklearn.preprocessing import Imputer

import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D


import db
import helper_functions
import optimization_trilateration
import locus
import itertools

pd.options.mode.chained_assignment = None  # default='warn'

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


	def init_from_database(self, beacon, gateways, start, end, label=None):
		database, cursor = db.connection()
		# query = "SELECT * FROM test_data WHERE tag_id = {} AND gateway_id = {} AND time_stamp >= {} AND time_stamp <= {}".format('%s', '%s', '%s', '%s')
		if label != None:
			query = "SELECT * FROM raw_data WHERE tag_id= {} AND label={}".format('%s', '%s')
			cursor.execute(query, [beacon, label])
		else:
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

	def slope_filter(self):
		rssis = []
		timestamps = []
		for record in self:
			rssis.append(record.rssi)
			timestamps.append(record.timestamp)
		#Get all max dist between time stamps (1m/s)
		#Then overwrite Rssis w/ filtered values
		fig=plt.figure(1)
		plt.plot(rssis, 'r')
		old_max_delta = 0
		for count in range(1, len(rssis)):
			curr_time = timestamps[count]
			last_time = timestamps[count - 1]
			time_delta = curr_time - last_time
			#Max speed 1m/s therefore no need for unit conversion. Conv from date time to float
			max_delta = time_delta.total_seconds()
			if (max_delta == 1) and (old_max_delta ==0.5):
				max_delta = 0.5
			if (max_delta == 0):
				max_delta = 0.5
			old_max_delta = max_delta
			last_dist = helper_functions.rssi_to_meter(rssis[count-1])
			rssis[count] = helper_functions.slope_limit_rssi(rssis[count], last_dist, max_delta )
		plt.plot(rssis,'b')
		plt.savefig('gif/' + str(record.gateway_id))
		plt.clf()
		copy_of_records = copy.deepcopy(self)

		for record, rssis in zip(copy_of_records, rssis ):
			record.rssi = rssis
		return copy_of_records


	def filter(self, window=None):
		rssis = []
		timestamps = []
		if window is None:
			window = 0
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


	def init_from_database(self, beacon, gateways, start, end, filter_length=None, slope_filter=False, label=None):
		self.gateway_list = gateways
		all_data = {}
		print gateways
		for gateway in gateways:
			print gateway
			records = ListOfRecords()

			records.init_from_database(beacon, gateway, start, end, label)
			if slope_filter:
				records = records.slope_filter() 
			if filter_length is not None:
				records = records.filter(filter_length)
			records = records.average_per_second()

			all_data[gateway] = records
			print 'Completed'

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


	def accuracy_of_classifier(self):
		data = np.array(self.data_frame[self.gateway_list])
		labels = np.array(self.data_frame['label'])		
		return self.classifier.score(data, labels)

	def predict(self):
		data = np.array(self.data_frame[self.gateway_list])
		return self.classifier.predict(data)

	def predict_proba(self):
		data = np.array(self.data_frame[self.gateway_list])
		return self.classifier.predict_proba(data)


		
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
		for label, c, m in zip(['1-1','1-2','1-3','1-4'], ['y', 'b', 'r', 'g'], ['x', '^', 'o', '*']):
			ts = self.data_frame.loc[self.data_frame['label'] == label]
			xs = ts[gateway_list[0]].values
			ys = ts[gateway_list[1]].values
			zs = ts[gateway_list[2]].values
			ax.scatter(xs, ys, zs, c=c, marker=m)

		ax.set_xlabel('X Label')
		ax.set_ylabel('Y Label')
		ax.set_zlabel('Z Label')		

	def two_d_plot(self, filename):
		"""hacky plotting for four categories and 3 gateways"""
		colors = itertools.cycle(["r", "b", "g", "k", "m", "y"])
		gateway_list = self.gateway_list
		for gateway in gateway_list:
			plt.plot(self.data_frame[gateway],color=next(colors))
		plt.savefig('gif/'+str(filename))
		plt.clf()

	def standardize(self):
		gateway_list=self.gateway_list
		for gateway in gateway_list:
			scaled = preprocessing.scale(self.data_frame[gateway])
			self.data_frame[gateway] = scaled


	# def replace_nan_imputer(self):
	# 	imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
	# 	gateway_list=self.gateway_list
	# 	for gateway in gateway_list:
	# 		imputed = imp.fit_transform(self.data_frame[gateway])
	# 		self.data_frame[gateway] = imputed
	def replace_nan(self):
		gateway_list=self.gateway_list
		numb_of_nan=0
		i=2
		for gateway in gateway_list:
			rssis = self.data_frame[gateway]
			if np.isnan(rssis[0]):
				rssis[0] = -60
			for row in range(1, (len(rssis)-1)):
				if np.isnan(rssis[row]):
					#print rssis[row]
					numb_of_nan = numb_of_nan+1
					last_value = rssis[row-1]
					#print last_value
					next_value = rssis[row+1]
					while np.isnan(next_value):
						if ((row+i)< len(rssis)):
							next_value = rssis[row+i]
							i = i+1
						else: next_value= last_value
					i = 2
					#print next_value
					rssis[row] = (last_value + next_value)/2
					#print rssis[row]
			self.data_frame[gateway] = rssis
			if np.isnan(rssis[row+1]):
				rssis[row+1] = rssis[row]
			#print rssis
		print "replaced",numb_of_nan,"elements containing NaN" 

			

	def _rename_label(self):
		matched_timestamps_merged =  copy.deepcopy(self)
		matched_timestamps_merged.data_frame = matched_timestamps_merged.data_frame.replace(['1-2', '1-3','1-4'],'1-1')
		matched_timestamps_merged.data_frame = matched_timestamps_merged.data_frame.replace(['2-2', '2-3','2-4'],'2-1')
		# matched_timestamps_merged.data_frame = matched_timestamps_merged.data_frame.replace(['3-2', '3-3','3-4'],'3-1')
		return matched_timestamps_merged
		
	def __repr__(self):

		return self.data_frame.__repr__()
		
if __name__ == "__main__":
	# EXAMPLE:

	# specify what beacon, gateway and timerange you're interested in
	# filter length=None means no filter
	# if you put filter=10 for example you will use moving average over 10 seconds
	matched_timestamps =  MatchedTimestamps()
	matched_timestamps.init_from_database('1', 
		['1', '2', '3'], 
		datetime(2017, 7, 13, 19, 40, 0), datetime(2017, 7, 13, 19, 40, 1), 
		filter_length=None)

	# print processed matched timestamp table
	print matched_timestamps.data_frame

	matched_timestamps.standardize()
	matched_timestamps.train_SVM()

	# predict itself
	print matched_timestamps.predict()


	
	# print matched_timestamps.train_SVM()
