# flaskLocus

# Running the flask application
1. Install flask: pip install flask
2. In /flaskLocus: export FLASK_APP=init.py
3. Flask run (Local) or Flask run -h 0.0.0.0 (Server?)


# Installing Python Dependencies
Install mysql
  sudo apt-get install python-mysqldb (linux)
  pip install MySQL-python (mac)
  
# Install MySQL
1. Install MySQL-serve: sudo apt-get install mysql-server (Linux) or download from MYSQL website (Mac)


# Logging into Database
1. Run in installed directory mysql -u root -p

# Create Local Database
1. Login using mysql -u root -p
2. CREATE DATABASE locus_development;
3. USE locus_development;
4. CREATE TABLE raw_data (time_stamp DATETIME(6), tag_id VARCHAR(50), gateway_id VARCHAR(50), rssi SMALLINT(10),  raw_packet_content VARCHAR(100));
