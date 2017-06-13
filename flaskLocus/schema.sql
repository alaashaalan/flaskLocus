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

DROP TABLE if exists app_state;
CREATE TABLE app_state (
	status BOOLEAN, 
	label VARCHAR(50)
);
INSERT INTO app_state (status) VALUES (0);
