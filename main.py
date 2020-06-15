# -*- encoding: utf-8 -*-
#!/usr/bin/env python3

import random

from flask import Flask, request, jsonify
import db

app = Flask(__name__, static_url_path = '', static_folder = 'client')
app.teardown_appcontext(db.del_conn)

#with open('client/index.html', 'r') as f:
#	index_html = f.read()

@app.route('/')
def index():
	with open('client/index.html', 'r') as f:
		index_html = f.read()
		
	return index_html

@app.route('/login', methods=['POST'])
def login():
    request_data = request.json
    user = db.get_user(request_data['userName'])

    return jsonify(user)

@app.route('/game_sessions')
def game_sessions():
    sessions = db.get_active_game_sessions()

    return jsonify(sessions)
    
@app.route('/game_session_players/<game_session_id>')
def game_session_players(game_session_id):
	
	players = db.get_game_session_players(game_session_id)
	
	return jsonify(players)
	
@app.route('/join_game', methods=['POST'])
def join_game():
    
    request_data = request.json

    db.insert_user_game_session(
        user_id = request_data['userId'],
        game_session_id = request_data['gameSessionId']
    )

    return jsonify([])
    
@app.route('/start_game_session', methods =['POST'])
def start_game_session():
	
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
	
	game_state_diffs = db.get_game_state_diffs(game_session_id, version)
	
	return jsonify(game_state_diffs)
	
@app.route('/create_game_session', methods = ['POST'])
def create_game_session():
	tstamp = request.json['tstamp']
	
	game_session_id = db.create_game_session(tstamp)
	
	return jsonify(game_session_id)

if __name__ == '__main__':
	app.run(port = 8080, debug = True)
