from flask import Flask, request, render_template, url_for, redirect
import helper_functions
import db
import datetime
import celery_app
import trilateration_mysql
from config import celery_config


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
	if request.form['button'] == 'start':
		label = request.form['label']
		status = 1
	if request.form['button'] == 'stop':
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


@app.route( '/timestamp_matching' , methods=[ 'GET']) 
def daily_processing():
	raise NotImplementedError