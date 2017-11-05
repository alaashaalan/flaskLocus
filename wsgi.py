from init import app
import logging

handler = logging.Filehandler('/var/log/flask_app.log')
handler.setLevel(logging.ERROR)
app.logger.addHandler(handler)

if __name__ == "__main__":
    app.run()