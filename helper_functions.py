from __future__ import division
import math
import db
import trilateration_mysql
import datetime

RSSI_1M = -60

def rssi_to_meter(rssi): #code works but will need some modification based what type of string we pass it
	RSSI_1m = RSSI_1M  #this value is experimentally measured
	distance = 10**((RSSI_1m - rssi)/20)
	return distance


def meter_to_rssi(meter): #code works but will need some modification based what type of string we pass it
	RSSI_1m = RSSI_1M  #this value is experimentally measured
	rssi = -20*(math.log10(meter)) + RSSI_1m
	return rssi


def slope_limit_rssi(current_rssi, last_distance, max_delta_distance):
	if (max_delta_distance>10):
		new_rssi = current_rssi
		return new_rssi

	min_rssi = meter_to_rssi(last_distance + max_delta_distance)

	if ((last_distance - max_delta_distance)<=0): 
		max_rssi = max(current_rssi, meter_to_rssi(last_distance))
	else: 
		max_rssi = meter_to_rssi(last_distance - max_delta_distance)

	if((min_rssi<=current_rssi) & (current_rssi<=max_rssi)):
		new_rssi = current_rssi
	elif(min_rssi>current_rssi):
		new_rssi = min_rssi
	else: 
		new_rssi = max_rssi
		
	return new_rssi



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


