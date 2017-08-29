import records
import pickle
import db

def create_model(beacon_id, gateway_id, start_date, end_date, filter_window, model_name):
	training_set =  records.MatchedTimestamps()

	training_set.init_from_database(beacon_id, gateway_id, start_date, end_date, 
		filter_length=filter_window)

	# print processed matched timestamp table
	training_set.replace_nan()
	training_set.remove_nan()
	training_set.standardize()
	training_set.train_SVM()
	
	'''
	# predict itself
	testing_set = records.MatchedTimestamps()
	testing_set.init_from_database(beacon_id, gateway_id, start_date, end_date, 
		filter_length=filter_window, label=test_label)

	training_classifier = training_set.classifier
	testing_set.classifier = training_classifier

	testing_prediction = testing_set.predict()
	print testing_prediction
	'''
	classifier = training_set.classifier
	classifier = pickle.dumps(classifier)

	return classifier

def use_model(beacon_id, gateway_id, start_date, end_date, filter_window, model_name, label):
	model = db.load_model(model_name)
	model = pickle.loads(model)
	print model

	predicting_set = records.MatchedTimestamps()
	predicting_set.init_from_database(beacon_id, gateway_id, start_date, end_date, 
		filter_length=filter_window, label=label)
	predicting_set.classifier = model
	prediction = predicting_set.predict()
	print prediction