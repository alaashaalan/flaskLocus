# flaskLocus

# SSH into server
`ssh -i locus.pem ubuntu@52.91.226.215`

# Running the flask application
for debug mode: `export FLASK_DEBUG=1`
1. In /flaskLocus: `export FLASK_APP=init.py`
2. `flask run` (Local) or `flask run -h 0.0.0.0` (Server)


# Installing Python Dependencies
Install flask: `pip install flask`
Install mysql>1.2.5
  `sudo apt-get install python-mysqldb` (linux)
  `pip install MySQL-python` (mac)
  
# Install MySQL
1. Install MySQL-server: `sudo apt-get install mysql-server` (Linux)

1. Install MySQL: `brew install mysql` (If brew isnt installed go to brew.sh)


# Logging into Database
1. Run  `mysql -u root -p` (-p for password if it exists)

# Testing Intake
```
curl -d '$GPRP,0CF3EE0B0BDD,CD2DA08685AD,-67,0201061AFF4C0002152F234454CF6D4A0FADF2F4911BA9FFA600000001C5,1496863953' http://localhost:5000/intake
```

# Create Local Database
1. Login using `mysql -u root -p`
2. `SOURCE flaskLocus/schema.sql`

# WIP

Celery and RabbitMQ
1. pip install celery
2. brew install rabbitmq

RabbitMQ
1. Create user credentials

Celery
1. celery -A init.celery beat
2. celery -A init.celery worker --loglevel=info
