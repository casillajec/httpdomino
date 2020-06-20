# -*- encoding: utf-8 -*-
#!/usr/bin/env python3

from flask import Blueprint, jsonify, request

import db

login_api = Blueprint('login_api', __name__)

@login_api.route('/login', methods = ['POST'])
def login():
	"""Log the user in.

	If the user is a first timer it will register it, in any case
	the function returns the user name and id.
	"""
	request_data = request.json
	user = db.get_user(request_data['userName'])

	return jsonify(user)
