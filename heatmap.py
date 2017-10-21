import matplotlib.cm as cm
from matplotlib.collections import PolyCollection
import matplotlib.pyplot as plt

import numpy as np

import pandas as pd

# import seaborn as sns; sns.set()

import db


NUM_OF_CLICKS = 0
ZONES = 0
POLYGONS = []
VERTICES = []

MAP_IMAGE = "992.png"
ALL_POLYGONS =[[(1606.5517015706805, 1107.9587696335079), (1603.8520942408372, 935.1839005235604), (1660.5438481675392, 935.1839005235604), (1657.8442408376959, 1105.2591623036651)], 
		[(1609.2513089005233, 916.28664921465986), (1609.2513089005233, 721.91492146596875), (1660.5438481675392, 721.91492146596875), (1660.5438481675392, 916.28664921465986)], 
		[(1606.5517015706805, 697.61845549738246), (1606.5517015706805, 514.04515706806296), (1663.243455497382, 514.04515706806296), (1665.9430628272248, 692.21924083769659)], 
		[(1611.9509162303661, 489.74869109947667), (1609.2513089005233, 314.27421465968609), (1663.243455497382, 314.27421465968609), (1663.243455497382, 495.14790575916254)], 
		[(1709.1367801047118, 1102.5595549738221), (1703.7375654450261, 935.1839005235604), (1760.4293193717276, 935.1839005235604), (1760.4293193717276, 1105.2591623036651)], 
		[(1709.1367801047118, 910.88743455497399), (1706.4371727748689, 716.51570680628288), (1755.0301047120415, 716.51570680628288), (1760.4293193717276, 910.88743455497399)], 
		[(1703.7375654450261, 694.91884816753941), (1706.4371727748689, 511.34554973822014), (1757.7297120418843, 514.04515706806296), (1760.4293193717276, 692.21924083769659)], 
		[(1709.1367801047118, 484.34947643979081), (1709.1367801047118, 319.67342931937196), (1765.8285340314133, 316.97382198952914), (1763.1289267015704, 492.44829842931949)]]

def onclick(event):
    global NUM_OF_CLICKS
    global POLYGONS, VERTICES

    NUM_OF_CLICKS = NUM_OF_CLICKS + 1

    ix, iy = event.xdata, event.ydata

    print 'x = %d, y = %d'%(
        ix, iy)
    
    VERTICES.append((ix,iy))

    if NUM_OF_CLICKS == 4: 
        NUM_OF_CLICKS = 0
        POLYGONS.append(VERTICES)
        VERTICES = []

    #len should be # of polys
    if len(POLYGONS) == ZONES: 
    	FIG.canvas.mpl_disconnect(CID)
    	plt.close()
    return 


def get_polygons(map_image, number_of_zones, new_zones=False):
	if new_zones == False:
		polygons = ALL_POLYGONS[0:number_of_zones]
		return polygons

	global FIG
	global CID
	global ZONES

	ZONES = number_of_zones

	FIG = plt.figure()
	ax = FIG.add_subplot(111)
	img = plt.imread(map_image, format='png')
	ax.imshow(img, zorder=0)

	CID= FIG.canvas.mpl_connect('button_press_event', onclick)
	plt.show()
	return POLYGONS


def store_heatmap(beacon_id, start_date, end_date, file_name=None, map_image=MAP_IMAGE, polygons=ALL_POLYGONS): 
	database, cursor = db.connection()

	# TODO: MAJOR THREAT!!!
	query = "SELECT * FROM zone_predictions where beacon_id='{}' and time_stamp>='{}' and time_stamp<='{}'".format(beacon_id, start_date, end_date)

	df = pd.read_sql(query, con=database)

	#get all unique locations, sort by #s then alpha. 
	unique_locations = pd.unique(df[['zone']].values.ravel())
	unique_locations = np.sort(unique_locations)

	freq = df.groupby('zone').agg({'beacon_id': len}).rename(columns={'beacon_id':'frequency'})
	# frequencies sorted by #s then alpha
	data = freq['frequency'].values
	print data
	max_freq = max(data) + 1
	min_freq = min(data) - 1
	norm = plt.Normalize(vmin=min_freq, vmax=max_freq)

	color = plt.cm.YlGn(norm(data))

	img = plt.imread(map_image, format='png')
	

	#convert each location to shape and coordinate for zone. 
	coll = PolyCollection(polygons, facecolors=color, edgecolors='none')
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.add_collection(coll)

	#plot background w/ zorder=0

	ax.imshow(img)

	# add a color bar
	color_bar = cm.ScalarMappable(cmap=cm.YlGn)
	color_bar.set_array(data)
	plt.colorbar(color_bar)

	cur_axes = plt.gca()
	cur_axes.get_xaxis().set_visible(False)
	cur_axes.get_yaxis().set_visible(False)

	#ax.autoscale_view()
	if file_name == None:
		plt.show()
	else:
		plt.savefig(file_name)
		return 



# def basic_heatmap(): 
# 	database, cursor = db.connection()
# 	df = pd.read_sql('SELECT * FROM zone_predictions', con=database)
# 	# Create a list of unique values by turning the
# 	# pandas column into a set
# 	#unique_locations = pd.unique(df[['zone']].values.ravel())
# 	freq = df.groupby('zone').agg({'beacon_id': len}).rename(columns={'beacon_id':'frequency'})
# 	print (freq)

# 	Index = ['1', '2', '3', '4']
# 	Cols = ['A', 'B']
# 	data = freq['frequency'].values
# 	#reshape number of index by number of cols
# 	data = data.reshape(4,2)
# 	hmap = pd.DataFrame(data, index=Index, columns=Cols)
# 	sns.heatmap(hmap,annot=True)


if __name__ == "__main__":
	
	# polygons = get_polygons(map_image, numb_of_zones, False)
	store_heatmap('1', '2017-07-13 19:40:00', '2017-07-13 19:40:02', 'heatmaps/test.jpg')