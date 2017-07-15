# http://www.alanzucconi.com/2017/03/13/positioning-and-trilateration/#part3

from scipy.optimize import minimize
import math
import matplotlib.pyplot as plt


def mse(x, locations, distances):
	"""
	Mean Square Error
	inputs:
	locations = [ (0,0), (0,10), (10,0), (10,10)]
	distances = [ 10,10, 10, 10]
	""" 
	mse = 0.0
	for location, distance in zip(locations, distances):
		distance_calculated = math.sqrt( (x[0] - location[0])**2 + (x[1] - location[1])**2 )
		mse += math.pow(distance_calculated - distance, 2.0)
	return mse / len(distances)

def initial_guess(locations, distances):
	min_dsit = min(distances)
	index_of_min_dist = distances.index(min_dsit)
	return locations[index_of_min_dist]


def trilaterate(locations, distances):
	"""
	optimization of trilataration
	"""
	# print locations, distances
	initial_guess_value = initial_guess(locations, distances)
	result = minimize(
		mse,                         # The error function
		initial_guess_value,            # The initial guess
		args=(locations, distances), # Additional parameters for mse
		method='L-BFGS-B',           # The optimisation algorithm
		options={
			'ftol':1e-10,         # Tolerance
			'maxiter': 1e+7      # Maximum iterations
		})
	location = result.x
	return location


def plotting(locations, distances, found_location):
	fig=plt.figure(1)
	plt.axis([-15,35,-15,35])
	ax=fig.add_subplot(1,1,1)

	circ=plt.Circle(found_location, radius=0.2, color='r', fill=True)
	ax.add_patch(circ)

	for dist, loc in zip(distances, locations):
		circ=plt.Circle(loc, radius=dist, color='g', fill=False)
		ax.add_patch(circ)

# def path_fit(self, found_location):
# 	a = [0,0]
# 	b = [10,0]
# 	c = [0,10]
# 	abc = []
# 	x = 0
# 	y = 0
# 	while (x < 10):
# 		abc.append(x,y)  
# 		x= x+.05
# 	while(y < 10):
# 		abc.append(x.y)
# 		x = x - .05
# 		y = y + .05
# 	while(y>=0):
# 		abc.append(x,y)
# 		y = y - .05
# return fitted_location

def plot_trilaterate(locations, distances, found_location):
	fig=plt.figure(1)
	plt.axis([-15,35,-15,35])
	ax=fig.add_subplot(1,1,1)

	circ=plt.Circle(found_location, radius=0.2, color='r', fill=True)
	#ax.add_patch(circ)

	for dist, loc in zip(distances, locations):
		circ=plt.Circle(loc, radius=dist, color='g', fill=False)
		#ax.add_patch(circ)

if __name__ == "__main__":
	locations = [ (0,0), (0,10), (5,5)]
	distances = [ 6, 6, 6] 

	found_location = trilaterate(locations, distances)
	plotting(locations, distances, found_location)


	plt.show()