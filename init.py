from flask import Flask, request, render_template, url_for, redirect
import helper_functions
import db
import datetime
import celery_app
from config import celery_config


app = Flask(__name__)

celery_config(app)
celery = celery_app.make_celery(app)

log = 'log'


@app.route('/', methods=['GET','POST']) 
def index():
	state, label = db.get_app_state()
	print state, label
	if state == 0:
		form = render_template('start_app.html', intake=state, label=label)
	else:
		form = render_template('stop_app.html', intake=state, label=label)
	return form


@app.route('/startstop', methods=['POST'])
def startstop():
	print('start stop')
	if request.form['button'] == 'start':
		label = request.form['label']
		status = 1
	if request.form['button'] == 'stop':
		label = None
		status = 0
	db.set_app_state(status, label)

	return redirect(url_for('index'))



@app.route('/intake', methods=['GET','POST'])
def intake():
	# read the current app status
	status, label = db.get_app_state()

	if status == 0:
		response = "app status is 0. Data not processed"
	else:	
		data = request.get_data()
		data = str(datetime.datetime.now()).split('.')[0]+',' + data + ',' + label
		processed_message = helper_functions.process_message(data)
		if processed_message:
			db.insert_raw_data(processed_message)
		response = data
	return response

@app.route('/gateway', methods=['GET','POST'])
def gateway():
	# read the current app status
	data = request.get_data()
	LOG_FILE = open(log, 'a+')
	LOG_FILE.write(data)
	LOG_FILE.close()
	return data


@app.route( '/login' , methods=[ 'GET' ,  'POST' ]) 
def login():
	if request.method ==  'POST' :
	 	do_the_login()
	else: 
		show_the_login_form()


@celery.task(name='celery_timestamp_matching')
def celery_timestamp_matching():
	helper_functions.timestamp_matching()
	return 'Data Processed successfully on' + str(datetime.datetime.now())
