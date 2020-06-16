# -*- encoding: utf-8 -*-
#!/usr/bin/env python3
""" Handle all DB transactions and manage connectios. """

from collections import defaultdict
from itertools import chain
import textwrap

from flask import g
import sqlite3

# Eventually we might want to implement a DB connection pool
# to avoid the overhead of creating one each time DB iteraction
# is needed, which is meant to be very often

def get_conn():
	"""Return DB connection object form g
	
	If there is none, create it.
	"""
	if 'conn' not in g:
		g.conn = sqlite3.connect(
			'db/domino.db',
			detect_types = sqlite3.PARSE_DECLTYPES
		)
		g.conn.row_factory = sqlite3.Row
		g.conn.execute('PRAGMA foreign_keys = ON;')

	return g.conn

def del_conn(e = None):
	"""Close DB connection.
	
	This method is called before a request gets sent.
	
	Args
	----
	e: notsure
		notsure
	"""
	conn = g.pop('conn', None)

	if conn is not None:
		conn.close()

def row2dict(row):
	"""Transform sqlite3.Row to dict."""
	return dict(zip(row.keys(), row))

def rows2dicts(rows):
	"""Transform list of sqlite3.Row s to list of dicts."""
	return list(map(row2dict, rows))
	
def rowtodic(row):
	"""Transform slqite3.Row to dict."""
	return dict(zip(row.keys(), row))
	
def lmap(func, it):
	"""List wrapper on map."""
	return list(map(func, it))

def get_user(user_name):
	"""Return user with name user_name.
	
	If no user with that name is found on the DB, it gets registered
	and returnted.
	
	Args
	----
	user_name: string
	
	Returns
	-------
	user: dict
	"""
	user_name = user_name.lower()
	
	conn = get_conn()
	c = conn.cursor()
	sql = textwrap.dedent('''\
		SELECT id, user_name
		FROM users
		WHERE user_name = ?;\
	''')
	c.execute(sql, (user_name,))
	user = c.fetchone()

	if user is None:
		sql = textwrap.dedent('''\
			INSERT INTO users(user_name)
			VALUES (?);
		''')
		c.execute(sql, (user_name,))
		c.execute('COMMIT;')
		user = {'id': c.lastrowid, 'user_name': user_name}
	else:
		user = rowtodic(user)

	return user

def get_active_game_sessions():
	"""Return active game session
	
	An active game session is one that is either WAITING to start
	or is currently OCCURING.
	
	Returns
	-------
	game_sessions: list(dict)
	"""
	conn = get_conn()
	c = conn.cursor()
	c.execute(textwrap.dedent('''\
		SELECT
			game_session.id as game_session_id,
			game_Status.val as game_status
		FROM game_session 
		LEFT JOIN game_status
			ON game_status.id = game_session.game_status_id
		WHERE game_status.val IN ('WAITING', 'OCCURING');\
	'''))
	game_sessions = rows2dicts(c.fetchall())
	gs_ids = [gs['game_session_id'] for gs in game_sessions]
	
	sql = textwrap.dedent('''\
		SELECT 
			player.game_session_id as game_session_id,
			users.user_name as user_name
		FROM player
		LEFT JOIN users ON users.id = player.user_id
		WHERE player.game_session_id IN ({});
	''')
	sql = sql.format(','.join('?' * len(gs_ids)))
	c.execute(sql, gs_ids)
	
	players = defaultdict(list)
	for p in rows2dicts(c.fetchall()):
		players[p['game_session_id']].append(p)
	c.close()
	
	for game_session in game_sessions:
		game_session['players'] = players[game_session['game_session_id']]

	return game_sessions
	
def get_game_session_players(game_session_id):
	"""Return players in a game_session.
	
	Args
	----
	game_session_id: int
	
	Returns
	-------
	players: list: dict
	"""
	conn = get_conn()
	c = conn.cursor()
	sql = textwrap.dedent('''\
		SELECT u.id, u.user_name
		FROM player p
		JOIN users u ON p.user_id = u.id
		WHERE p.game_session_id = ?
		ORDER BY turn ASC;\
	''')
	
	c.execute(sql, (game_session_id,))
	players = rows2dicts(c.fetchall())
	c.close() 
	
	return players

def insert_user_game_session(user_id, game_session_id):
	"""Insert an user into a game_session.
	
	Args
	----
	user_id: int
	game_session_id: int
	"""
	conn = get_conn()
	c = conn.cursor()
	sql = textwrap.dedent('''\
		SELECT turn
		FROM player
		WHERE game_session_id = ?
		ORDER BY turn DESC
		LIMIT 1;\
	''')
	c.execute(sql, (game_session_id,))
	last_player = c.fetchone()
	
	if last_player is None:
		last_player = {'turn' : -1 }
	
	sql = textwrap.dedent('''\
		INSERT INTO player(user_id, game_session_id, turn)
		VALUES (?, ?, ?)
		ON CONFLICT(user_id, game_session_id) DO NOTHING;\
	''')
	c.execute(sql, (user_id, game_session_id, last_player['turn'] + 1))
	c.execute('COMMIT;')
	c.close()
	
def get_stone_enums():
	""" Return all stone enums. """
	
	c = get_conn().cursor()
	c.execute(textwrap.dedent('''\
		SELECT id, val
		FROM stone;
	'''))
	stones = rows2dicts(c.fetchall())
	c.close()
	
	return stones

def get_last_game_state_diff(game_session_id):
	"""Return the last diff of a game_session.
	
	Args
	----
	game_session_id: int
	
	Returns
	-------
	game_state_diff: dict
	"""
	c = get_conn().cursor()
	
	sql = textwrap.dedent('''\
		SELECT gsd.version, gsd.user_id, s.val, p.val
		FROM game_state_diff gsd
		LEFT JOIN stone s ON s.id = gsd.stone_id
		LEFT JOIN placement p ON p.id = gsd.placement_id
		WHERE gsd.game_session_id = ?
		ORDER BY gsd.version DESC
		LIMIT 1;
	''')
	c.execute(sql, (game_session_id,))
	game_state_diff = c.fetchone()
	if game_state_diff:
		game_state_diff = rowtodic(game_state_diff)
		
	c.close()
	
	return game_state_diff
	
def get_next_player(game_session_id):
	"""Return the player that goes next in a game session.
	
	Args
	----
	game_session_id: int
	
	Returns
	-------
	next_player: dict
	"""
	c = get_conn().cursor()
	
	sql = textwrap.dedent('''\
		SELECT u.id, u.user_name
		FROM player p
		LEFT JOIN users u ON p.user_id = u.id
		WHERE p.game_session_id = ?
		  AND p.turn = 1 + (SELECT p.turn
							FROM game_state_diff
							WHERE game_session_id = ?
							ORDER BY version DESC
							LIMIT 1) % 4;
	''')
	c.execute(sql, (game_session_id, game_session_id))
	
	next_player = c.fetchone()
	if next_player:
		next_player = rowtodic(next_player)
	c.close()
	
	return next_player

def get_game_state_diffs(game_session_id, version):
	"""Return all diffs of game_session starting at specified version.
	
	Args
	----
	game_session_id: int
	version: int
	
	Returns
	------
	game_state_diffs: list(dict)
	"""
	c = get_conn().cursor()
	
	sql = textwrap.dedent('''\
		SELECT
			gsd.version,
			gsd.user_id,
			s.val as stone,
			p.val as placement
		FROM game_state_diff gsd
		LEFT JOIN stone s ON s.id = gsd.stone_id
		LEFT JOIN placement p ON p.id = gsd.placement_id
		WHERE gsd.game_session_id = ? AND gsd.version > ?
		ORDER BY gsd.version ASC;
	''')
	c.execute(sql, (game_session_id, version))
	game_state_diffs = lmap(rowtodic, c.fetchall())
	c.close()
	
	return game_state_diffs

def assign_stones_player(user_id, game_session_id, stone_ids):
	"""Assigns initial stones to a player.
	
	Args
	----
	user_id: int
	game_session_id: int
	stone_ids: list(int)
	"""
	c = get_conn().cursor()
	
	sql = textwrap.dedent('''\
		INSERT INTO player_has_stone (user_id, game_session_id, stone_id)
		VALUES {}
		ON CONFLICT (user_id, game_session_id, stone_id) DO NOTHING;\
	'''. format(','.join(['(?, ?, ?)'] * len(stone_ids))))
	values = [(user_id, game_session_id, sid) for sid in stone_ids]
	c.execute(sql, tuple(chain(*values)))
	c.execute('COMMIT;')
	c.close()
	
def mark_game_session_started(game_session_id):
	""" Mark specified game_session as OCCURING on DB. """
	c = get_conn().cursor()
	
	sql = textwrap.dedent('''\
		SELECT id
		FROM game_status
		WHERE val = 'OCCURING';\
	''')
	c.execute(sql)
	occuring_id = c.fetchone()['id']
	
	sql = textwrap.dedent('''\
		UPDATE game_session
		SET game_status_id = ?
		WHERE id = ?;
	''')
	c.execute(sql, (occuring_id, game_session_id))
	
	c.execute('COMMIT;')
	
	c.close()
	
def get_game_session_status(game_session_id):
	"""Return the status of specified game_session.
	
	Args
	----
	game_session_id: int
	
	Returns
	-------
	game_session_status: str
	"""
	c = get_conn().cursor()
	
	sql = textwrap.dedent('''\
		SELECT gst.val
		FROM game_session gs
		LEFT JOIN game_status gst ON gst.id = gs.game_status_id
		WHERE gs.id = ?;\
	''')
	c.execute(sql, (game_session_id,))
	game_session_status = c.fetchone()
	c.close()
	
	return game_session_status['val']
	
def get_player_stones(game_session_id, user_id):
	"""Return the stones that a player starts with.
	
	Args
	----
	game_session_id: int
	user_id: int
	
	Returns
	-------
	player_stones: list(str)
	"""
	c = get_conn().cursor()
	
	sql = textwrap.dedent('''\
		SELECT st.val
		FROM player_has_stone phs
		LEFT JOIN stone st ON st.id = phs.stone_id
		WHERE phs.game_session_id = ? AND phs.user_id = ?;\
	''')
	
	c.execute(sql, (game_session_id, user_id))
	stones = c.fetchall()
	player_stones = [stone['val'] for stone in stones]
	c.close()
	
	return player_stones
	
def game_session_has_diffs(game_session_id):
	""" Return wether the specified game session has diffs. """
	c = get_conn().cursor() 
	
	sql = textwrap.dedent('''\
		SELECT COUNT(*) > 0
		FROM game_state_diff
		WHERE game_session_id = ?
	''')
	c.execute(sql, (game_session_id,))
	has_diffs = c.fetchone()
	c.close()
	
	return has_diffs

def create_game_session(tstamp):
	"""Create a new, empty game session and return it's id."""
	c = get_conn().cursor()
	
	c.execute(textwrap.dedent('''\
		SELECT id
		FROM game_status
		WHERE val = 'WAITING';
	'''))
	waiting_id = c.fetchone()['id']
	
	sql = textwrap.dedent('''\
		INSERT INTO game_session(game_status_id, tstamp)
		VALUES (?, ?);
	''')
	c.execute(sql, (waiting_id, tstamp))
	c.execute('COMMIT;')	
	game_session_id = c.lastrowid
	
	c.close()
	
	return game_session_id
	
def register_play(game_session_id, user_id, stone, placement, tstamp):
	""" Register a play that a player made.
	
	Args
	----
	game_session_id: int
	user_id: int
	stone: str
	placement: str
	tstamp: int
	"""
	c = get_conn().cursor()
	
	stone_id = None
	if stone:
		sql = textwrap.dedent('''\
			SELECT id
			FROM stone
			WHERE val = ?;\
		''')
		c.execute(sql, (stone,))
		stone_id = c.fetchone()['id']
	
	placement_id = None
	if placement:
		sql = textwrap.dedent('''\
			SELECT id
			FROM placement
			WHERE val = ?;\
		''')
		c.execute(sql, (placement,))
		placement_id = c.fetchone()['id']
		
	last_diff = get_last_game_state_diff(game_session_id)
	if last_diff:
		version = last_diff['version'] + 1
	else:
		version = 1
		
	sql = textwrap.dedent('''\
		INSERT INTO game_state_diff(game_session_id, version, user_id, stone_id, placement_id, tstamp)
		VALUES (?, ?, ?, ?, ?, ?);
	''')
	c.execute(sql, (game_session_id, version, user_id, stone_id, placement_id, tstamp))
	c.execute('COMMIT;')
	
	c.close()
	
		
	
