# HTTP Domino

A web-based implementation of the popular Domino game using only HTTP requests

## DB initialization

Create a file as `db/domino.db` with sqlite3 and run schema.sql and init.sql on it, you may do:

	.../db&> sqlite3 domino.db
	sqlite3> .read schema.sql
	sqlite3> .read init.sql
