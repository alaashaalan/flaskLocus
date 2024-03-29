DROP TABLE if exists raw_data;
CREATE TABLE raw_data (
	id INT NOT NULL AUTO_INCREMENT,
	time_stamp DATETIME(6),  
	tag_id VARCHAR(50), 
	gateway_id VARCHAR(50), 
	rssi SMALLINT(10), 
	raw_packet_content VARCHAR(100),
	ntp INT(11),
	label VARCHAR(100),
	PRIMARY KEY (id)
);

DROP TABLE if exists classifiers;
CREATE TABLE classifiers (
	id INT NOT NULL AUTO_INCREMENT,
	classifier_name VARCHAR(50),  
	classifier longblob,
	gateway_list blob,
	standardize_scalar blob,
	PRIMARY KEY (id)
);

DROP TABLE if exists app_state;
CREATE TABLE app_state (
	status BOOLEAN, 
	label VARCHAR(50)
);
DROP TABLE if exists zone_predictions;
CREATE TABLE zone_predictions (
	id INT NOT NULL AUTO_INCREMENT,
	time_stamp DATETIME(6),
	beacon_id VARCHAR(50),
	zone VARCHAR(50),
	PRIMARY KEY (id)

);
INSERT INTO app_state (status) VALUES (0);
