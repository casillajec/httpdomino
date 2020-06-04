CREATE TABLE IF NOT EXISTS stone (
	id    SERIAL,
	value TEXT   NOT NULL,

	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS placement (
	id    SERIAL,
	value TEXT   NOT NULL,

	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS game_status (
	id    SERIAL,
	value TEXT   NOT NULL,

	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS users (
	id SERIAL,
	name TEXT NOT NULL,

	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS game_session (
	id             SERIAL,
	game_status_id BIGINT    NOT NULL,
	tstamp         TIMESTAMP NOT NULL,

	PRIMARY KEY (id),

	FOREIGN KEY (game_status_id)
		REFERENCES game_status (id)
);

CREATE TABLE IF NOT EXISTS player (
	user_id         BIGINT NOT NULL,
	game_session_id BIGINT NOT NULL,

	PRIMARY KEY (user_id, game_session_id),

	FOREIGN KEY (user_id)
		REFERENCES users (id),
	FOREIGN KEY (game_session_id)
		REFERENCES game_session (id)
);

CREATE TABLE IF NOT EXISTS player_has_stone (
	user_id         BIGINT NOT NULL,
	game_session_id BIGINT NOT NULL,
	stone_id        BIGINT NOT NULL,

	PRIMARY KEY (user_id, game_session_id, stone_id),

	FOREIGN KEY (user_id, game_session_id)
		REFERENCES player (user_id, game_session_id),
	FOREIGN KEY (stone_id)
		REFERENCES stone (id)
);

CREATE TABLE IF NOT EXISTS game_state_diff (
	game_session_id BIGINT    NOT NULL,
	version         INT       NOT NULL,
	user_id         BIGINT    NOT NULL,
	stone_id        BIGINT,
	placement_id    BIGINT    NOT NULL,
	tstamp          TIMESTAMP NOT NULL,

	PRIMARY KEY (game_session_id, version),

	FOREIGN KEY (game_session_id)
		REFERENCES game_session (id),
	FOREIGN KEY (user_id, game_session_id)
		REFERENCES player (user_id, game_session_id),
	FOREIGN KEY (stone_id)
		REFERENCES stone (id),
	FOREIGN KEY (placement_id)
		REFERENCES placement (id)
);
