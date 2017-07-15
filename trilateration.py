import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import date2num

import random

import db
import helper_functions
import locus
import trilateration2d
import optimization_trilateration
import trilateration_mysql

MIN_NUMBER_OF_GATEWAYS_FOR_TRIANGULATION = 3
AVERAGING_WINDOW = 5

class point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def to_array(self):
        return [self.x, self.y]

class Trilateration():
	def __init__(self, location, beacon_id, gateway_ids, start_time, end_time):
		self.location = location
		self.beacon_id = beacon_id
		self.gateway_ids = gateway_ids
		self.start_time = start_time
		self.end_time = end_time

		self.matched_timestamps = []


		self.data_per_gateway = {}  # e.g. self.data_per_gateway[0] all records for gateway_ids[0] etc
		for gateway in self.gateway_ids:
			current_records = db.find_by_tag_id_gateway_id_date_range('raw_data', '*', self.beacon_id, gateway, self.start_time, self.end_time)
			self.data_per_gateway[gateway] = np.array(current_records)
			# print self.data_per_gateway[gateway]


	def trilaterate(self):
		
														#get time delta for all 
		# for gateway in self.gateway_ids:
		# 	self._get_deltas(self.data_per_gateway[gateway])

		# run slope limitation & remove outliers
		for gateway in self.gateway_ids:
			self._slope_filter(self.data_per_gateway[gateway])


		# smooth rssi using running average
		for gateway in self.gateway_ids:
			#print gateway
			new_rssi_list = []
			for ind, record in enumerate(self.data_per_gateway[gateway]):
				rssi = record[3]
				# new_rssi = np.random.normal(record[3], 0)
				new_rssi = record[3]
				new_rssi_list.append(new_rssi)
				# print rssi, new_rssi
				record[3] = new_rssi
			print(np.std(new_rssi_list))
			plt.figure(2)
			plt.plot(new_rssi_list)
			plt.figure(1)

			self._moving_average(self.data_per_gateway[gateway], AVERAGING_WINDOW)


		# create a dictionary of matched timestamps
		self.matched_timestamps = self._records_for_second()

		# get coordinates of all base stations
		gateway_coordinates = []
		for gateway in self.location.list_of_gateways:
			#gateway_coordinates.append(gateway.to_point())
			gateway_coordinates.append(gateway.to_point().to_array())         #this one for optimization

		locations = []	
		images = []
		for ind, time in enumerate(self.find_unique_timestamps()):
			# print time
			record = self.matched_timestamps[time]

			if len(self.matched_timestamps[time]) < MIN_NUMBER_OF_GATEWAYS_FOR_TRIANGULATION:
				print "not enough gateways"
				continue

			# convert rssis to meters
			distances = []
			for gateway in self.gateway_ids:
				if len(record[gateway]) != 0:
					rssi = np.average(record[gateway])
					# print rssi
					# rssi = np.random.normal(rssi, 4)
					distances.append(helper_functions.rssi_to_meter(rssi))
			# print distances

			#print(gateway_coordinates)


			# actual trilateration
			#center = trilateration_mysql.trilateration(gateway_coordinates, distances)
			
			# r2 approx. 
			center = optimization_trilateration.trilaterate(gateway_coordinates, distances)
			# print center
			
			locations.append(center)
			# fig=plt.figure(1)
			# plt.ion()
			# plt.show()
			plt.clf()
			optimization_trilateration.plotting(gateway_coordinates, distances, center)		#r2 optimized plotting
			#optimization_trilateration.plot_trilaterate(gateway_coordinates, distances, center)

			# plt.plot([5, 5], [0, 10], color='k', linestyle='-', linewidth=1)
			plt.legend(distances)

			plt.savefig('gif/' + str(ind))
			# images.append(imageio.imread('gif/' + str(ind) + '.png'))
		
			
			
			# plt.draw()
		# kargs = { 'duration': 0.1 }
		# imageio.mimsave('gif/trilateration.gif', images, **kargs)
		plt.show()

	

	def find_unique_timestamps(self):
		timestamps = set([])

		for gateway in self.data_per_gateway:
			gateway_data = self.data_per_gateway[gateway]
			for row in gateway_data:
				timestamps.add(row[0])

		return sorted(timestamps)

	# def _get_deltas(self, records):

	# 	timestamps = []
	# 	delta = []

	# 	for record in records:					
	# 		timestamps.append(record[0])

	# 	for count in range(1, len(timestamps)):
	# 		curr_time = timestamps[count]
	# 		last_time = timestamps[count - 1]
	# 		time_delta = curr_time - last_time
	# 		#Max speed 1m/s therefore no need for unit conversion. Conv from date time to float
	# 		max_delta = time_delta.total_seconds()
	# 		delta.append(max_delta)

	# 	print(len(delta))
	# 	for count in range(len(delta) - 1):
	# 		i = 1
	# 		#get numb of adv in this second
	# 		if (delta[count+1] == 0):
	# 			while (delta[count+i] == 0):
	# 				if ((count+i+1) >= len(delta)):
	# 					print("end")
	# 					break
	# 				print(count)
	# 				print(i)
	# 				i = i+1
	# 			num_per_sec = i 
	# 			delt = 1 / num_per_sec
	# 		#assign delta values to the second
	# 		while (i >= 1):
	# 			delta[(count + i - 1) ] = delt
	# 			i = i -1
		
	# 													#need to modify this to create a new column

	# 	for time_deltas, record in zip(timestamps, records):
	# 		record[0] = time_deltas			




	def _slope_filter(self, records):
		rssis = []
		timestamps = []
		#Get all Rssi & Time stamps
		for record in records:					
			rssis.append(record[3])
			timestamps.append(record[0])
		#Get all max dist between time stamps (1m/s)
		#Then overwrite Rssis w/ filtered values
		for count in range(1, len(rssis)):
			curr_time = timestamps[count]
			last_time = timestamps[count - 1]
			time_delta = curr_time - last_time
			#Max speed 1m/s therefore no need for unit conversion. Conv from date time to float
			max_delta = time_delta.total_seconds()
			last_dist = helper_functions.rssi_to_meter(rssis[count-1])
			rssis[count] = helper_functions.slope_limit_rssi(rssis[count], last_dist, max_delta )
	
		for filt_rssi, record in zip(rssis, records):
			record[3] = filt_rssi

	def _moving_average(self, records, window):
		# TODO: need to average based on last and next N seconds, not last and next N records
		rssis = []
		timestamps = []
		for record in records:
			rssis.append(record[3])
			timestamps.append(record[0])

		# modes = ['full', 'same', 'valid']
		averaged_rssi = np.convolve(rssis, np.ones((window,))/window, mode='valid')
		new_rssi_list = []
		for avg_rssi, record in zip(averaged_rssi, records):
			record[3] = avg_rssi
			new_rssi_list.append(avg_rssi)

		return np.std(new_rssi_list)

	def plot_rssis(self, gateway):
		rssis = []
		timestamps = []
		for rec in self.data_per_gateway[gateway]:
			rssis.append(rec[3])
			timestamps.append(rec[0])

		dates = date2num(timestamps)
		plt.plot_date(dates, rssis)
		plt.gcf().autofmt_xdate()	
		# plt.plot(rssis)


	def _records_for_second(self):
		rssi_per_second = {}
		for timestamp in self.find_unique_timestamps():
			rssis = {}
			for gateway in self.gateway_ids:
				rssis[gateway] = []
				for record in self.data_per_gateway[gateway]:
					if record[0] >= timestamp and record[0] <= timestamp:
						rssis[gateway].append(record[3])



			rssi_per_second[timestamp] = rssis
		return rssi_per_second





if __name__ == '__main__':

	#location = locus.Location('location_park.json')

	
	location = locus.Location('location_park.json')

	beacon = location.list_of_beacons[3]
	gateway_ids = location.get_all_gateway_ids()


	# a = Trilateration(location, beacon, gateway_ids, datetime.datetime(2017, 5, 29, 16, 48, 00), datetime.datetime(2017, 5, 29, 16, 54, 59))
	# a = Trilateration(location, beacon, gateway_ids, datetime.datetime(2017, 6, 02, 00, 00, 00), datetime.datetime(2017, 6, 03, 16, 54, 59))


	# park first test
	# a = Trilateration(location, beacon, gateway_ids, datetime.datetime(2017, 6, 03, 00, 5, 00), datetime.datetime(2017, 6, 03, 00,6, 00))


	# park second test try:
	a = Trilateration(location, beacon, gateway_ids, datetime.datetime(2017, 6, 03, 00, 10, 00), datetime.datetime(2017, 6, 03, 00 ,12, 00))

	#a = Trilateration(location, beacon, gateway_ids, datetime.datetime(2017, 6, 02, 23, 37, 00), datetime.datetime(2017, 6, 02, 23 ,45, 00))
	# a = Trilateration(location, beacon, gateway_ids, datetime.datetime(2017, 5, 30, 12, 01, 59), datetime.datetime(2017, 5, 30, 12, 02, 32))

	a.trilaterate()


