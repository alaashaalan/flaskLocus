# from celery.schedules import crontab

def credentials():

	host="localhost"
	user="root"
	passwd="12345"
	db="locus_development"

	db_credentials = {
		'host' : host,
		'user' : user,
		'passwd' : passwd,
		'db' : db
	}

	return db_credentials

# All times are in UTC
# def celery_config(app):
# 	app.config.update(
# 		ENABLE_UTC=True,
# 		Timezone='UTC',
# 		CELERY_BROKER_URL='amqp://guest:guest@localhost:5672//',
# 		CELERY_RESULT_BACKEND='amqp://',

# 		CELERYBEAT_SCHEDULE={
# 			'celery_timestamp_matching': {
# 				'task': 'celery_timestamp_matching',
# 				'schedule': crontab(hour=5, minute=0)
# 			}
# 		}
# 	)

# 	return