# -*- encoding: utf-8 -*-
#!/usr/bin/env python3

import random

from flask import Blueprint, jsonify, request

import db
from constants import TOTAL_STONES

preboard_api = Blueprint('preboard_api', __name__)

@preboard_api.route('/game_session_players/<game_session_id>')
def game_session_players(game_session_id):
	"""Return players in a game session."""
	
	players = db.get_game_session_players(game_session_id)
	
	return jsonify(players)
	
def register_initial_distribution(game_session_id):
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

@preboard_api.route('/start_game_session', methods = ['POST'])
def start_game_session():
	"""Start a game session
	
	Distribute the initial stones among the players and resturn
	a response with the player's current stones and the names of all
	the players.
	
	This endpoint will receive a request per client but it may
	only be distribute once, therefore the first time it is executed
	it marks the game session as 'OCCURING', we shall pray that's
	safe enough.
	"""
	request_data = request.json
	game_session_id = request_data['gameSessionId']
	user_id = request_data['userId']
	
	game_session_status = db.get_game_session_status(game_session_id)
	
	if game_session_status != 'OCCURING':
		db.mark_game_session_started(game_session_id)
		register_initial_distribution(game_session_id)
	
	players = db.get_game_session_players(game_session_id)
	player_names = [p['user_name'] for p in players]
	
	# Might not have been assigned yet
	player_stones = []
	while len(player_stones) != TOTAL_STONES/len(players):
		player_stones = db.get_player_stones(game_session_id, user_id)
		
	diffs = db.get_game_state_diffs(game_session_id, 0)
	for diff in filter(lambda d: d['user_id'] == user_id, diffs):
		player_stones.remove(diff['stone'])
	 
	return jsonify({
		'player_stones': player_stones,
		'player_names': player_names
	})
