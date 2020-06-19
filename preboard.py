# -*- encoding: utf-8 -*-
#!/usr/bin/env python3

import random

from flask import Blueprint, jsonify, request

import db

preboard_api = Blueprint('preboard_api', __name__)

@preboard_api.route('/game_session_players/<game_session_id>')
def game_session_players(game_session_id):
	"""Return players in a game session."""
	
	players = db.get_game_session_players(game_session_id)
	
	return jsonify(players)

@preboard_api.route('/start_game_session', methods = ['POST'])
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
