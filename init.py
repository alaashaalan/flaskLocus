from flask import Flask, request
from helper_functions import process_message
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
	processed_message = process_message(data)
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