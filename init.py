from flask import Flask, request, render_template, url_for, redirect
from flask import jsonify
import random

import helper_functions
import db
import datetime
import celery_app
from config import celery_config
import classifiers


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

@app.route('/setup_classifier', methods=['POST', 'GET'])
def setup_classifier():
	return render_template('setup_classifier.html')

@app.route('/init_classifier', methods=['POST'])
def init_classifier():
	# Collect data from request form (ASSUMES IS PROPER DATA)
	# start_date = request.form['start_date']
	# end_date = request.form['end_date']
	start_date = '2017-07-13 19:40:00'
	end_date = '2017-07-13 19:40:02'
	beacon_id = request.form['beacon_id']
	gateway_id = request.form['gateway_id']
	filter_window = request.form['filter_window']
	classifier_name = request.form['classifier_name']


	# Process Data into correct form to run SVM
	start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
	end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")	
	gateway_id = [whitespace.strip() for whitespace in gateway_id.split(',')]

	if filter_window == '0' or filter_window == 'None':
		filter_window = None
	else:
		filter_window = int(filter_window)

	print beacon_id, gateway_id, start_date, end_date, filter_window, classifier_name

	# Train SVM and check results
	classifier = classifiers.create_classifier(beacon_id, gateway_id, start_date, end_date, filter_window, classifier_name)
	db.save_classifier(classifier, classifier_name)

	return render_template('use_classifier.html')

@app.route('/use_classifier', methods=['POST', 'GET'])
def use_classifier():
	return render_template('use_classifier.html')

@app.route('/predict_classifier', methods=['POST'])
def predict_classifier():

	# Collect data from request form (ASSUMES IS PROPER DATA)
	start_date = request.form['start_date']
	end_date = request.form['end_date']
	start_date = '2017-07-13 19:40:00'
	end_date = '2017-07-13 19:40:02'	
	beacon_id = request.form['beacon_id']
	gateway_id = request.form['gateway_id']
	label = request.form['label']
	filter_window = request.form['filter_window']
	classifier_name = request.form['classifier_name']

	# start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
	# end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")	
	gateway_id = [whitespace.strip() for whitespace in gateway_id.split(',')]

	if filter_window == '0' or filter_window == 'None':
		filter_window = None
	else:
		filter_window = int(filter_window)

	result = classifiers.use_classifier(beacon_id, gateway_id, start_date, end_date, filter_window, classifier_name, label)
	return str(result)



@app.route('/real_time', methods=['GET']) 
def real_time():
	return render_template('real_time.html')



@app.route('/classify', methods=['POST'])
def classify():

	start_date = '2017-07-13 19:40:00'
	end_date = '2017-07-13 19:40:02'	

	# end_date = datetime.datetime.now()
	# end_date = end_date + datetime.timedelta(hours=7)  # convert to UTC
	# start_date = end_date - datetime.timedelta(seconds=1)
	# end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')
	# start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
	
	beacon_id = 1
	gateway_id = [1,2,3]

	filter_window = None
	label = None

	classifier_name = 'test10'

	result = classifiers.use_classifier(beacon_id, gateway_id, start_date, end_date, filter_window, classifier_name, label)
	print result
	return jsonify({
    	'class': 'class' + str(result) +  str(random.randint(1,9))})


	