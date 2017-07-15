import json

class Location:
	"""
	e.g. a specific store, or the lab 
	"""
	def __init__(self, json_config_file):

		self.list_of_gateways = []
		self.list_of_beacons = []
		self.name = None

		with open(json_config_file) as location_file:    
			location_data = json.load(location_file)
		self.name = location_data['name']

		for gateway in location_data['gateways']:
			self.list_of_gateways.append(Gateway(gateway['id'], gateway['x'], gateway['y']))

		self.list_of_beacons = location_data['beacons']

	def get_all_gateway_ids(self):
		list_of_gateway_ids = []
		for gw in self.list_of_gateways:
			list_of_gateway_ids.append(gw.id)
		return list_of_gateway_ids


	def trilaterate(self):
		raise NotImplementedError


class Gateway:
	def __init__(self, gateway_id, x, y):
		self.id = gateway_id
		self.x = x
		self.y = y

	def to_point(self):
		return trilateration2d.point(self.x, self.y)


if __name__ == '__main__':
	lab = Location('location.json')
	print(lab.list_of_beacons)