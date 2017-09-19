import records
import db

def create_classifier(beacon_id, gateway_id, start_date, end_date, filter_window, classifier_name):
	training_set =  records.MatchedTimestamps()

	training_set.init_from_database(beacon_id, gateway_id, start_date, end_date, 
		filter_length=filter_window)

	print training_set

	# training_set.replace_nan()
	# training_set.remove_nan()
	# training_set.standardize()
	# print training_set
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

	return classifier

def use_classifier(beacon_id, gateway_id, start_date, end_date, filter_window, classifier_name, label):
	classifier = db.load_classifier(classifier_name)
	
	predicting_set = records.MatchedTimestamps()
	predicting_set.init_from_database(beacon_id, gateway_id, start_date, end_date, 
		filter_length=filter_window, label=label)

	# print processed matched timestamp table
	# predicting_set.replace_nan()
	# predicting_set.remove_nan()
	# predicting_set.standardize()
	# print predicting_set

	predicting_set.classifier = classifier
	prediction = predicting_set.predict()

	return prediction