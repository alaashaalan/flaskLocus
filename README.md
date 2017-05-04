# flaskLocus

# Running the flask application
1. Install flask: `pip install flask`
2. In /flaskLocus: `export FLASK_APP=init.py`
3. `flask run` (Local) or `flask run -h 0.0.0.0` (Server?)


# Installing Python Dependencies
Install mysql
  `sudo apt-get install python-mysqldb` (linux)
  `pip install MySQL-python` (mac)
  
# Install MySQL
1. Install MySQL-server: `sudo apt-get install mysql-server` (Linux)

1. Install MySQL: `brew install mysql` (If brew isnt installed go to brew.sh)


# Logging into Database
1. Run in installed directory `mysql -u root -p` (-p for password if it exists)

# Testing Intake
```
curl -d '$GPRP,5826D8AF76AB,D897B89C7B2F,-98,02011A07FF4C0010020B00' http://localhost:5000/intake
```

# Create Local Database
1. Login using `mysql -u root -p`
2. `CREATE DATABASE locus_development;`
3. `USE locus_development;`
4. `CREATE TABLE raw_data (id INT NOT NULL AUTO_INCREMENT, time_stamp DATETIME(6), tag_id VARCHAR(50), gateway_id VARCHAR(50), rssi SMALLINT(10),  raw_packet_content VARCHAR(100) , PRIMARY KEY (id));`
