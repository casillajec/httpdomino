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
    
@app.route('/get_stone_distribution/<game_session_id>')
def start_game_session(game_session_id):
	
	players = db.get_game_session_players(game_session_id)
	n_players = len(players)
	
	stones = db.get_stone_enums()
	n_stones = len(stones)
	random.shuffle(stones)
	
	stone_distribution = {}
	hand_size = int(n_stones/n_players)
	for i, player in enumerate(players):
		stone_distribution[player['user_name']] = stones[i*hand_size:(i+1)*hand_size]
	
	return jsonify(stone_distribution)

if __name__ == '__main__':
	app.run(port = 8080, debug = True)
