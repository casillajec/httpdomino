# -*- encoding: utf-8 -*-
#!/usr/bin/env python3
"""Main."""

import random

from flask import Flask, request, jsonify

import db
from login import login_api

app = Flask(__name__, static_url_path = '', static_folder = 'client')
app.teardown_appcontext(db.del_conn)
app.register_blueprint(login_api)

#with open('client/index.html', 'r') as f:
#	index_html = f.read()

@app.route('/')
def index():
	"""Return index.html file as text."""
	with open('client/index.html', 'r') as f:
		index_html = f.read()
		
	return index_html

@app.route('/game_sessions')
def game_sessions():
	"""Return available game sessions."""
	sessions = db.get_active_game_sessions()

	return jsonify(sessions)
	
@app.route('/game_session_players/<game_session_id>')
def game_session_players(game_session_id):
	"""Return players in a game session."""
	
	players = db.get_game_session_players(game_session_id)
	
	return jsonify(players)
	
@app.route('/join_game', methods=['POST'])
def join_game():
	"""Register an user as a player on a game session."""
	
	request_data = request.json

	db.insert_user_game_session(
		user_id = request_data['userId'],
		game_session_id = request_data['gameSessionId']
	)

	return jsonify([])
	
@app.route('/start_game_session', methods = ['POST'])
def start_game_session():
	"""Start a game session
	
	It distributes the initial stones among the players.
	
	This endpoint might receive a request per client but it may
	only be executed once, therefore the first time it is executed
	it marks the game session as 'OCCURING' and we shall pray that's
	safe enough.
	"""
	request_data = request.json
	game_session_id = request_data['gameSessionId']
	
	# Check if it has already been started
	game_session_status = db.get_game_session_status(game_session_id)
	if game_session_status == 'OCCURING':
		return jsonify([])
		
	db.mark_game_session_started(game_session_id)
	
	# Distribute stone among players
	players = db.get_game_session_players(game_session_id)
	n_players = len(players)
	
	stones = db.get_stone_enums()
	n_stones = len(stones)
	random.shuffle(stones)
	
	stone_distribution = {}
	hand_size = int(n_stones/n_players)
	for i, player in enumerate(players):
		player_stones = stones[i*hand_size:(i+1)*hand_size]
		player_stone_ids = [s['id'] for s in player_stones]
		db.assign_stones_player(player['id'], game_session_id, player_stone_ids)
	
	return jsonify([])
	
@app.route('/get_player_stones/<game_session_id>/<user_id>')
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
@app.route('/register_play', methods=['POST'])
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
		print('last_diff:', last_diff)
		print('request_data:', request_data)
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
	
@app.route('/get_game_state_diffs/<game_session_id>/<version>')
def get_game_state_diffs(game_session_id, version):
	"""Return diffs from specified version up until the most recent."""
	
	game_state_diffs = db.get_game_state_diffs(game_session_id, version)
	
	return jsonify(game_state_diffs)
	
@app.route('/create_game_session', methods = ['POST'])
def create_game_session():
	"""Return the id of a new and empty game session."""
	tstamp = request.json['tstamp']
	
	game_session_id = db.create_game_session(tstamp)
	
	return jsonify(game_session_id)

if __name__ == '__main__':
	app.run(port = 8080, debug = True)
