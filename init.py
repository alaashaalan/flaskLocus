from flask import Flask, request
import helper_functions
import db
import datetime
import trilateration_mysql


app = Flask(__name__)

log = 'log'

@app.route('/') 
def index():
	return  'Index Page'

@app.route('/intake', methods=['GET','POST'])
def intake():
	data = request.get_data()
	data = str(datetime.datetime.now()).split('.')[0]+','+data 
	processed_message = helper_functions.process_message(data)
	if processed_message:
		db.insert_raw_data(processed_message)

	f = open(log, 'a')
	f.write(data)  
	f.close()
	
	return data


@app.route( '/login' , methods=[ 'GET' ,  'POST' ]) 
def login():
	if request.method ==  'POST' :
	 	do_the_login()
	else: 
		show_the_login_form()



@app.route('/timestamp_matching', methods=['GET'])
def timestamp_matching():
	"""
	TODO: this needs to be scheduled somehow. 
	"""
	start_time = '2017-04-28 00:45:52'
	end_time = '2017-04-28 00:51:14'
	tag_id = "0CF3EE0B0BDD"
	gateway_ids = ["D897B89C7B2F","FF9AE92EE4C9","CD2DA08685AD"]

	start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
	end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

	result = trilateration_mysql.timestamp_matching(start_time, end_time, tag_id, gateway_ids)
	return  str(result)

@app.route('/plot_points', methods=['GET'])
def plot_points():
	start_time = '2017-04-28 00:45:52'
	end_time = '2017-04-28 00:51:14'
#	tag_id = "0CF3EE0B0BDD"

	start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
	end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

#	result = db.plot_points(start_time, end_time, tag_id)
	result = db.plot_points(start_time, end_time)
	return 
