# -*- encoding: utf-8 -*-
#!/usr/bin/env python3

from flask import Blueprint, jsonify, request

import db

board_api = Blueprint('board_api', __name__)

@board_api.route('/get_player_stones/<game_session_id>/<user_id>')
def get_player_stones(game_session_id, user_id):
	"""Return a player's stones on a particular game session.
	
	Also return the name of the players, this endpoint is requested 
	when the client enters a board (game session starts) and maybe
	it should be named differently because it should also return
	the amount of stones each player has.
	
	But now that I think about it, that's silly, each player starts with
	a constant amount of stones and each diff might remove one,
	which is something that we should be able to easily calculate.
	
	That's why documenting is so useful, you can figure stuff out
	that would have otherwise been a pain.
	
	Anyway, it should be renamed, consider something like
	'get_client_initial_state', because what it returns should
	vary depending on which client (user) is making the request.
	"""
	player_stones = db.get_player_stones(game_session_id, user_id)
	players = db.get_game_session_players(game_session_id)
	player_names = [p['user_name'] for p in players]
	 
	return jsonify({
		'player_stones': player_stones,
		'player_names': player_names
	})
	
# TODO NEEDS TO BE TESTED
@board_api.route('/register_play', methods=['POST'])
def register_play():
	"""Register a play from a player that just made it's play."""
	request_data = request.json
	
	if db.game_session_has_diffs(request_data['gameSessionId']):
		next_player = db.get_next_player(request_data['gameSessionId'])
		last_diff = db.get_last_game_state_diff(request_data['gameSessionId'])
		
		# Check if the player making the move is the corresponding player
		if next_player and next_player['id'] != request_data['userId']:
			return jsonify([])  # ??? TODO
		
		# Check if the version matches with last version
		if last_diff and last_diff['version'] != request_data['version']:
			return jsonify([])  # ??? TODO
	
	# Do we check that the move was actually correct or should we
	# just trust the untrusty client?
	
	# Register the move
	placement = request_data.get('placement')
	db.register_play(
		game_session_id = request_data['gameSessionId'],
		user_id = request_data['userId'],
		stone = request_data.get('stone'),
		placement = placement.upper() if placement else placement,
		tstamp = request_data['tstamp']
	)
	
	return jsonify([])
	
@board_api.route('/get_game_state_diffs/<game_session_id>/<version>')
def get_game_state_diffs(game_session_id, version):
	"""Return diffs from specified version up until the most recent."""
	
	game_state_diffs = db.get_game_state_diffs(game_session_id, version)
	
	return jsonify(game_state_diffs)
