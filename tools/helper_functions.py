from __future__ import division
import math

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

def path_rules(prediction, probabilities, positions):
	"""
	if the diff between current and next guess by more than 1 zone,
	then look for the next best probable zone
	"""

	numb_of_corrections =0
	last_num = 500
	for item in range(len(probabilities)-1):
		t = 1
		cur_pos  = prediction[item]
		cur_row = int(cur_pos[0])
		cur_col = int(cur_pos[2])

		next_pos = prediction[item+1]
		next_row = int(next_pos[0])
		next_col = int(next_pos[2])


		next_prob = probabilities[item+1]
		next_prob_sorted = sorted(probabilities[item+1], key=int, reverse=True)

		while (abs(next_row-cur_row)>1) or (abs(next_col-cur_col)>1): 
			next_best_guess = next_prob_sorted[t]
			for location in range(len(next_prob)):
				if next_best_guess == next_prob[location]: 
					next_pos = positions[location]
			next_row = int(next_pos[0])
			next_col = int(next_pos[2])
			t = t+1
		if t>1: 
			if abs(last_num - item) ==1:
				numb_of_corrections+=1
				last_num=item
			else: 
				numb_of_corrections=0
		next_pos = str(next_row)
		next_pos+='-'
		next_pos+=str(next_col)
		if numb_of_corrections < 2:
			prediction[item+1] = next_pos
		else: 
			numb_of_corrections=0

	print prediction

# Accepts 2D lists or tuples and flattens them into the corresponding structure
def flatten_2d_struct(struct_2d):
	return [element for struct_1d in struct_2d for element in struct_1d]






