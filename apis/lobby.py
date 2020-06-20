# -*- encoding: utf-8 -*-
#!/usr/bin/env python3

from flask import Blueprint, jsonify, request

import db

lobby_api = Blueprint('lobby_api', __name__)

@lobby_api.route('/game_sessions')
def game_sessions():
	"""Return available game sessions."""
	sessions = db.get_active_game_sessions()

	return jsonify(sessions)

@lobby_api.route('/join_game', methods=['POST'])
def join_game():
	"""Register an user as a player on a game session."""
	
	request_data = request.json

	db.insert_user_game_session(
		user_id = request_data['userId'],
		game_session_id = request_data['gameSessionId']
	)

	return jsonify([])

@lobby_api.route('/create_game_session', methods = ['POST'])
def create_game_session():
	"""Return the id of a new and empty game session."""
	tstamp = request.json['tstamp']
	
	game_session_id = db.create_game_session(tstamp)
	
	return jsonify(game_session_id)
