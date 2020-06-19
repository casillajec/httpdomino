# -*- encoding: utf-8 -*-
#!/usr/bin/env python3
"""Main."""

from flask import Flask, request, jsonify

import db
from login import login_api
from lobby import lobby_api
from preboard import preboard_api
from board import board_api

app = Flask(__name__, static_url_path = '', static_folder = 'client')
app.teardown_appcontext(db.del_conn)
app.register_blueprint(login_api)
app.register_blueprint(lobby_api)
app.register_blueprint(preboard_api)
app.register_blueprint(board_api)

#with open('client/index.html', 'r') as f:
#	index_html = f.read()

@app.route('/')
def index():
	"""Return index.html file as text."""
	with open('client/index.html', 'r') as f:
		index_html = f.read()
		
	return index_html

if __name__ == '__main__':
	app.run(port = 8080, debug = True)
