from __future__ import division
import math
import db
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

# def path_rules(prediction, probabilites, positions):
# 	for item in range(len(probabilites)-1):
# 		t = 1
# 		cur_pos  = prediction[item]
# 		cur_row = int(cur_pos[0])
# 		cur_col = int(cur_pos[2])
		
# 		next_pos = prediction[item+1]
# 		next_row = int(next_pos[0])
# 		next_col = int(next_pos[2])

# 		next_prob = probabilites[item+1]
# 		next_prob_sorted = sorted(probabilites[item+1], key=int, reverse=True)

# 		while (abs(next_row-cur_row)>1) or (abs(next_col-cur_col)>1): 
# 			next_best_guess = next_prob_sorted[t]
# 			for location in range(len(next_prob)):
# 				if next_best_guess == next_prob[location]: 
# 					next_pos = positions[location]
# 			next_row = int(next_pos[0])
# 			next_col = int(next_pos[2])
# 			t = t+1
# 		next_pos = str(next_row)
# 		next_pos+='-'
# 		next_pos+=str(next_col)
# 		prediction[item+1] = next_pos
# 	return prediction

def path_rules(prediction, probabilites, positions):
	for item in range(len(probabilites)-1):
		cur_pos  = prediction[item]
		next_pos = prediction[item+1]
		changes = 0
		u = zip(cur_pos, next_pos)
		for i, j in u: 
			if i != j:
				changes = changes +1
		if changes >1: 
			row = cur_pos[0]
			col = cur_pos[2]
			guesses = probabilites[item+1]
			guesses_sorted = sorted(probabilites[item+1], key=int, reverse=True)
			next_best_guess =guesses_sorted[1]
			for i in range(len(guesses)):
				if next_best_guess == guesses[i]:
					location = i
			prediction[item+1]= positions[location]
			#print "changed item", item+2
		changes =0
	return prediction