from flask import Flask, request
import helper_functions
import db
import datetime


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
	start_time = '2017-05-01 17:30:20'
	end_time = '2017-05-01 17:30:25'
	tag_id = "5826D8AF76AB"
	gateway_ids = ["1","2","3"]

	start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
	end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

	result = helper_functions.timestamp_matching(start_time, end_time, tag_id, gateway_ids)
	return  str(result)