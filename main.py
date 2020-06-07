# -*- encoding: utf-8 -*-
#!/usr/bin/env python3

from flask import Flask, request, jsonify
import db

app = Flask(__name__, static_url_path = '', static_folder = 'client')

#with open('client/index.html', 'r') as f:
#	index_html = f.read()

@app.route('/')
def index():
	with open('client/index.html', 'r') as f:
		index_html = f.read()
		
	return index_html

if __name__ == '__main__':
	app.run(port = 8080, debug = True)
