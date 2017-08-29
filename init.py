from flask import Flask, request, render_template, url_for, redirect
from flask import jsonify
import random

import helper_functions
import db
import datetime
import celery_app
from config import celery_config
from data_process import train_SVM, predict_SVM


app = Flask(__name__)

celery_config(app)
celery = celery_app.make_celery(app)


@app.route('/', methods=['GET','POST']) 
def index():
	state = db.get_app_state()
	label = db.get_app_label()
	if state == 0:
		form = render_template('start_app.html', intake=state, label=label)
	else:
		form = render_template('stop_app.html', intake=state, label=label)
	return form


@app.route('/startstop', methods=['POST'])
def startstop():
	if request.form['button'] == 'Start':
		label = request.form['label']
		status = 1
	if request.form['button'] == 'Stop':
		label = None
		status = 0
	db.set_app_state(status, label)

	return redirect(url_for('index'))


@app.route('/intake', methods=['POST'])
def intake():
	# check if allowed
	if not db.get_app_state():
		return ("app status is 0. Data not processed\n", 403)
	else:	
		data = request.get_data()
		db.insert_multiple_messages(data)
	return (data + '\n', 200)

@app.route('/training_setup', methods=['POST', 'GET'])
def training_setup():
	return render_template('training_setup.html')

@app.route('/training_result', methods=['POST'])
def training_result():
	# Collect data from request form (ASSUMES IS PROPER DATA)
	start_date = request.form['start_date']
	end_date = request.form['end_date']
	beacon_id = request.form['beacon_id']
	gateway_id = request.form['gateway_id']
	filter_window = request.form['filter_window']
	test_label = request.form['test_label']


	# Process Data into correct form to run SVM
	start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
	end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")	
	gateway_id = [whitespace.strip() for whitespace in gateway_id.split(',')]
	filter_window = int(filter_window)

	# Train SVM and check results
	run_SVM(beacon_id, gateway_id, start_date, end_date, filter_window, test_label)

	return render_template('training_result.html')


@app.route('/timestamp_matching' , methods=[ 'GET']) 
def daily_processing():
	raise NotImplementedError



@app.route('/real_time', methods=['GET']) 
def real_time():
	return render_template('real_time.html')



@app.route('/classify', methods=['POST'])
def classify():

	# beacon_id = request.form['beacon']
	# gateway_id = request.form['gateways'].split(',')
	# end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	# end_date = end_date + datetime.timedelta(hours=7)  # convert to UTC
	# start_date = end_date - datetime.timedelta(seconds=1)
	# classifier = request.form['classifier']
	# filter_window = 1


	# prediction = predict_SVM(beacon_id, gateway_id, start_date, end_date, filter_window, classifier)


	return jsonify({
    	'class': 'class' + str(random.randint(1,9))})

	