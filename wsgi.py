import logging
import os
os.environ['PRODUCTION'] = "True"
from taigadash.app import app

gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.DEBUG)
app.logger.debug('Iniciando App...')