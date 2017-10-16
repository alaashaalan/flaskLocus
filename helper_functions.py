from __future__ import division
import math
import db
import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from scipy.misc import imread

RSSI_1M = -60
number_of_clicks = 0
verts = []
coords = []

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

def onclick(event):
    global ix, iy, number_of_clicks
    number_of_clicks = number_of_clicks +1
    ix, iy = event.xdata, event.ydata
    print 'x = %d, y = %d'%(
        ix, iy)
    global verts, coords
    coords.append((ix,iy))
    if (number_of_clicks == 4): 
        number_of_clicks = 0
        verts.append(coords)
        coords = []
    #len should be # of polys
    if len(verts) ==zones: 
    	fig.canvas.mpl_disconnect(cid)
    	plt.close()
    return 

def get_polys(number_of_zones, new_zones=False):
	if (new_zones == False):
		all_verts =[[(1606.5517015706805, 1107.9587696335079), (1603.8520942408372, 935.1839005235604), (1660.5438481675392, 935.1839005235604), (1657.8442408376959, 1105.2591623036651)], 
				[(1609.2513089005233, 916.28664921465986), (1609.2513089005233, 721.91492146596875), (1660.5438481675392, 721.91492146596875), (1660.5438481675392, 916.28664921465986)], 
				[(1606.5517015706805, 697.61845549738246), (1606.5517015706805, 514.04515706806296), (1663.243455497382, 514.04515706806296), (1665.9430628272248, 692.21924083769659)], 
				[(1611.9509162303661, 489.74869109947667), (1609.2513089005233, 314.27421465968609), (1663.243455497382, 314.27421465968609), (1663.243455497382, 495.14790575916254)], 
				[(1709.1367801047118, 1102.5595549738221), (1703.7375654450261, 935.1839005235604), (1760.4293193717276, 935.1839005235604), (1760.4293193717276, 1105.2591623036651)], 
				[(1709.1367801047118, 910.88743455497399), (1706.4371727748689, 716.51570680628288), (1755.0301047120415, 716.51570680628288), (1760.4293193717276, 910.88743455497399)], 
				[(1703.7375654450261, 694.91884816753941), (1706.4371727748689, 511.34554973822014), (1757.7297120418843, 514.04515706806296), (1760.4293193717276, 692.21924083769659)], 
				[(1709.1367801047118, 484.34947643979081), (1709.1367801047118, 319.67342931937196), (1765.8285340314133, 316.97382198952914), (1763.1289267015704, 492.44829842931949)]]
		for i in range(number_of_zones):
			verts.append(all_verts[i])
		return verts
	global fig
	global cid
	global zones
	zones = number_of_zones

	fig = plt.figure()
	ax = fig.add_subplot(111)
	img = imread("992.png")
	ax.imshow(img, zorder=0)
	for i in xrange(0,1):
		cid= fig.canvas.mpl_connect('button_press_event', onclick)
	plt.show()
	return verts




