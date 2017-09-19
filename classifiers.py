import records
import db

def create_classifier(beacon_id, gateway_list, start_date, end_date, filter_window, classifier_name):
	training_set =  records.MatchedTimestamps()

	training_set.init_from_database(beacon_id, gateway_list, start_date, end_date, 
		filter_length=filter_window)

	# print processed matched timestamp table
	training_set.replace_nan()
	training_set.remove_nan()
	training_set.standardize_training()
	training_set.train_SVM()

	return training_set.classifier, training_set.standardize_scalar

def use_classifier(beacon_id, start_date, end_date, filter_window, classifier_name, label):
	classifier, gateway_list, standardize_scalar  = db.load_classifier(classifier_name)
	
	predicting_set = records.MatchedTimestamps()
	predicting_set.init_from_database(beacon_id, gateway_list, start_date, end_date, 
		filter_length=filter_window, label=label)
	predicting_set.classifier = classifier
	predicting_set.replace_nan()
	predicting_set.remove_nan()
	predicting_set.standardize_testing(standardize_scalar)
	prediction = predicting_set.predict()

	return prediction