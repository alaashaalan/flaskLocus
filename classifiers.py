import records
import db

def create_classifier(beacon_id, gateway_id, start_date, end_date, filter_window, classifier_name):
	training_set =  records.MatchedTimestamps()

	training_set.init_from_database(beacon_id, gateway_id, start_date, end_date, 
		filter_length=filter_window)

	# print processed matched timestamp table
	training_set.replace_nan()
	training_set.remove_nan()
	training_set.standardize()
	training_set.train_SVM()

	classifier = training_set.classifier

	return classifier

def use_classifier(beacon_id, start_date, end_date, filter_window, classifier_name, label):
	classifier, gateway_list = db.load_classifier(classifier_name)
	
	predicting_set = records.MatchedTimestamps()
	predicting_set.init_from_database(beacon_id, gateway_list, start_date, end_date, 
		filter_length=filter_window, label=label)
	predicting_set.classifier = classifier
	predicting_set.replace_nan()
	predicting_set.remove_nan()
	predicting_set.standardize()
	prediction = predicting_set.predict()

	return prediction