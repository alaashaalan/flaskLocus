import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import date2num

import db

class Trilateration():
	def __init__(self, beacon, gateways, start_time, end_time):
		self.beacon_ids = beacon
		self.gateway_ids = gateways


		self.data_per_gateway = {}  # e.g. self.data_per_gateway[0] all records for gateway_ids[0] etc
		for gateway in self.gateway_ids:
			current_records = db.find_by_tag_id_gateway_id_date_range('raw_data', '*', beacon, gateway, start_time, end_time)
			self.data_per_gateway[gateway] = np.array(current_records)


	def trilaterate(self):
		# smooth rssi using running average
		for gateway in self.gateway_ids:
			self._moving_average(self.data_per_gateway[gateway], 20)







	def _moving_average(self, records, window):
		# TODO: need to average based on last and next N seconds, not last and next N records
		rssis = []
		timestamps = []
		for record in records:
			rssis.append(record[3])
			timestamps.append(record[0])

		averaged_rssi = np.convolve(rssis, np.ones((window,))/window, mode='same')

		for avg_rssi, record in zip(averaged_rssi, records):
			record[3] = avg_rssi

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





	def split_into_seconds():
		pass

	def timestamp_matching():
		pass

	def trilateration():
		pass

if __name__ == '__main__':
	beacon = '0CF3EE0B08CA'
	gateway_ids = ['D897B89C7B2F']
	a = Trilateration(beacon, gateway_ids, datetime.datetime(2017, 5, 9, 22, 54, 31), datetime.datetime(2017, 5, 10, 22, 54, 31))
	a.plot_rssis(gateway_ids[0])
	plt.figure()
	a.trilaterate()

	a.plot_rssis(gateway_ids[0])
	plt.show()
