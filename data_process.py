import records

def train_SVM(beacon_id, gateway_id, start_date, end_date, filter_window, test_label):
	training_set =  records.MatchedTimestamps()

	training_set.init_from_database(beacon_id, gateway_id, start_date, end_date, 
		filter_length=filter_window)

	# print processed matched timestamp table
	training_set.replace_nan()
	training_set.remove_nan()
	training_set.standardize()
	training_set.train_SVM()

	# predict itself
	testing_set = records.MatchedTimestamps()
	testing_set.init_from_database(beacon_id, gateway_id, start_date, end_date, 
		filter_length=filter_window, label=test_label)

	training_classifier = training_set.classifier
	testing_set.classifier = training_classifier

	testing_prediction = testing_set.predict()
	print testing_prediction


def predict_SVM(beacon_id, gateway_id, start_date, end_date, filter_window, classifier):

	prediction_set =  records.MatchedTimestamps()
	prediction_set.init_from_database(beacon_id, gateway_id, start_date, end_date, 
		filter_length=filter_window)

	# TODO: retrieve the classifier
	prediction_set.classifier = classifier

	prediction = prediction_set.predict()
	return prediction
