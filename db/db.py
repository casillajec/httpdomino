# -*- encoding: utf-8 -*-
#!/usr/bin/env python3

import queue
import sqlite3

# Eventually we might want to implement a DB connection pool
# to avoid the overhead of creating one each time DB iteraction
# is needed, which is meant to be very often
MAX_CONNECTIONS = 12
pool = queue.Queue()

def conn():
    return sqlite3.connect('domino.db')

