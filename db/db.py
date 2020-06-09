# -*- encoding: utf-8 -*-
#!/usr/bin/env python3

from collections import defaultdict
import textwrap

from flask import g
import sqlite3

# Eventually we might want to implement a DB connection pool
# to avoid the overhead of creating one each time DB iteraction
# is needed, which is meant to be very often
MAX_CONNECTIONS = 12

def get_conn():
	if 'conn' not in g:
		g.conn = sqlite3.connect(
			'db/domino.db',
			detect_types = sqlite3.PARSE_DECLTYPES
		)
		g.conn.row_factory = sqlite3.Row
		g.conn.execute('PRAGMA foreign_keys = ON;')

	return g.conn

# What is e?
def del_conn(e = None):
	conn = g.pop('conn', None)

	if conn is not None:
		conn.close()

def row2dict(row):
	return dict(zip(row.keys(), row))

def rows2dicts(rows):
	return list(map(row2dict, rows))

def get_user(user_name):

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
		user = row2dict(user)

	return user

def get_active_game_sessions():
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
	
	conn = get_conn()
	c = conn.cursor()
	sql = textwrap.dedent('''\
		SELECT u.user_name
		FROM player p
		JOIN users u ON p.user_id = u.id
		WHERE p.game_session_id = ?;\
	''')
	c.execute(sql, (game_session_id,))
	players = rows2dicts(c.fetchall())
	c.close() 
	
	return players

def insert_user_game_session(user_id, game_session_id):

	conn = get_conn()
	c = conn.cursor()
	sql = textwrap.dedent('''\
		INSERT INTO player(user_id, game_session_id)
		VALUES (?, ?)
		ON CONFLICT(user_id, game_session_id) DO NOTHING;\
	''')
	c.execute(sql, (user_id, game_session_id))
	c.execute('COMMIT;')
	c.close()
	
def get_stone_enums():
	
	c = get_conn().cursor()
	c.execute(textwrap.dedent('''\
		SELECT val
		FROM stone;
	'''))
	stones = rows2dicts(c.fetchall())
	c.close()
	
	stones = [s['val'] for s in stones]
	
	return stones
	
