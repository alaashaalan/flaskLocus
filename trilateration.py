import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import imageio
import random

import db
import helper_functions
import locus
import trilateration2d
import optimization_trilateration

MIN_NUMBER_OF_GATEWAYS_FOR_TRIANGULATION = 3
AVERAGING_WINDOW = 30

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
		# smooth rssi using running average
		for gateway in self.gateway_ids:
			print gateway
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
			# plt.show()

			print self._moving_average(self.data_per_gateway[gateway], AVERAGING_WINDOW)


		# create a dictionary of matched timestamps
		self.matched_timestamps = self._records_for_second()

		# get coordinates of all base stations
		gateway_coordinates = []
		for gateway in self.location.list_of_gateways:
			gateway_coordinates.append(gateway.to_point().to_array())
		

		# print gateway_coordinates

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

			# center = trilateration2d.trilateration(gateway_coordinates, distances)
			center = optimization_trilateration.trilaterate(gateway_coordinates, distances)
			# print center
			
			locations.append(center)
			# fig=plt.figure(1)
			# plt.ion()
			# plt.show()
			plt.clf()
			optimization_trilateration.plotting(gateway_coordinates, distances, center)
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


	# def timestamp_matching(self):
	# 	x_y_coordinates = {}
	# 	for timestamp in self.find_unique_timestamps():
			

		# 	for gateway in self.gateway_ids:
			# 	print gateway
			# 	rssis_for_this_second[gateway] = []
			# 	for record in self.data_per_gateway[gateway]:
			# 		if record[0] >= timestamp and record[0] <= timestamp:
			# 			rssis_for_this_second[gateway].append(record[3])
			# 			print rssis_for_this_second[gateway]

			# 	if len(rssis_for_this_second[gateway]) == 0:
			# 		print 'found zero rssis for this gateway for this second! scipping this timestamp'
			# 		break
			# 	else:
			# 		rssis_for_this_second[gateway] = np.average(rssis_for_this_second[gateway])
			# 	print rssis_for_this_second[gateway]

			# print len(rssis_for_this_second), len(self.gateway_ids)
			# if len(rssis_for_this_second) != len(self.gateway_ids):
			# 	print "couldn't find matching timestamps for all gateways"
			# 	continue
			# else:
			# 	averaged_rssis_for_this_second = []
			# 	for gateway in self.gateway_ids:
			# 		averaged_rssis_for_this_second.append(rssis[gateway])

			# 	self.matched_timestamps.append([timestamp] + averaged_rssis_for_this_second)


if __name__ == '__main__':

	location = locus.Location('location_park.json')
	# print location.list_of_beacons
	beacon = location.list_of_beacons[0]
	gateway_ids = location.get_all_gateway_ids()

	# a = Trilateration(location, beacon, gateway_ids, datetime.datetime(2017, 5, 29, 16, 48, 00), datetime.datetime(2017, 5, 29, 16, 54, 59))
	# a = Trilateration(location, beacon, gateway_ids, datetime.datetime(2017, 6, 02, 00, 00, 00), datetime.datetime(2017, 6, 03, 16, 54, 59))


	# park first test
	# a = Trilateration(location, beacon, gateway_ids, datetime.datetime(2017, 6, 03, 00, 5, 00), datetime.datetime(2017, 6, 03, 00,6, 00))


	# park second test try:
	a = Trilateration(location, beacon, gateway_ids, datetime.datetime(2017, 6, 03, 00, 10, 00), datetime.datetime(2017, 6, 03, 00,11, 00))


	# a = Trilateration(location, beacon, gateway_ids, datetime.datetime(2017, 5, 30, 12, 01, 59), datetime.datetime(2017, 5, 30, 12, 02, 32))

	# print(a.data_per_gateway[gateway_ids[0]])     
	# print a.find_unique_timestamps()
	# print a._records_for_second()
	# a.plot_rssis(gateway_ids[0])
	# plt.figure()
	a.trilaterate()

	# a.plot_rssis(gateway_ids[0])
	# plt.ylim(ymax = -70, ymin = -100)
	# plt.show()
