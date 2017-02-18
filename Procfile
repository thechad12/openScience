web: gunicorn -w 4 -b 0.0.0.0:$PORT -k gevent app:app
init: python models.py
upgrade: python db_upgrade.py
