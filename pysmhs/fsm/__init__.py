import logging
import logging.handlers

logger_mdb = logging.getLogger('pymdb')
logger_mdb.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(
    'pymdb.log', maxBytes=1028576, backupCount=10)
form = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)s:%(message)s')
handler.setFormatter(form)
logger_mdb.addHandler(handler)

logger_kiosk = logging.getLogger('kiosk')
logger_kiosk.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(
    'kiosk.log', maxBytes=1028576, backupCount=10)
form = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)s:%(message)s')
handler.setFormatter(form)
logger_kiosk.addHandler(handler)