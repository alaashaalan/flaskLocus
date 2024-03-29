from flask import Flask, request, render_template, url_for, redirect, send_file
import helper_functions
import db
import datetime
import celery_app
from config import celery_config
import classifiers

import heatmap

app = Flask(__name__)

# celery_config(app)
# celery = celery_app.make_celery(app)


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

@app.route('/setup_classifier', methods=['POST', 'GET'])
def setup_classifier():
	return render_template('setup_classifier.html')

@app.route('/init_classifier', methods=['POST'])
def init_classifier():
	# Collect data from request form (ASSUMES IS PROPER DATA)
	start_date = request.form['start_date']
	end_date = request.form['end_date']
	beacon_id = request.form['beacon_id']
	gateway_list = request.form['gateway_list']
	classifier_name = request.form['classifier_name']


	# Process Data into correct form to run SVM
	start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
	end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")	
	gateway_list = [whitespace.strip() for whitespace in gateway_list.split(',')]

	# Train SVM and check results
	classifier, standardize_scalar = classifiers.create_classifier(beacon_id, gateway_list, start_date, end_date, classifier_name)
	db.save_classifier(classifier, classifier_name, gateway_list, standardize_scalar)

	return render_template('use_classifier.html')

@app.route('/use_classifier', methods=['POST', 'GET'])
def use_classifier():
	return render_template('use_classifier.html')

@app.route('/predict_classifier', methods=['POST'])
def predict_classifier():

	# Collect data from request form (ASSUMES IS PROPER DATA)
	start_date = request.form['start_date']
	end_date = request.form['end_date']
	beacon_id = request.form['beacon_id']
	classifier_name = request.form['classifier_name']

	start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
	end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")	

	results = classifiers.use_classifier(beacon_id, start_date, end_date, classifier_name)

	file_name = 'static/test.jpg'
	heatmap.store_heatmap(beacon_id, start_date, end_date, file_name)
	return send_file('static/test.jpg')





@app.route('/timestamp_matching' , methods=[ 'GET']) 
def daily_processing():
	raise NotImplementedError
