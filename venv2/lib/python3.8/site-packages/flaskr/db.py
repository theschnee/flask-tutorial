import sqlite3
import click
from flask import current_app, g

# method to get database 
def get_db():
	if 'db' not in g:
		g.db = sqlite3.connect(
			current_app.config['DATABASE'],
			detect_types=sqlite3.PARSE_DECLTYPES
		)
		g.db.row_factory = sqlite3.Row
	
	return g.db

# method to close database
def close_db(e=None):
	db = g.pop('db',None)

	if db is not None:
		db.close()

# initialize database and run sql commands from schema.sql
def init_db():
	db = get_db()
	
	with current_app.open_resource('schema.sql') as f:
		db.executescript(f.read().decode('utf-8'))

# calls init_db and shows success/failure to user 
@click.command('init-db')
def init_db_command():
	"""Clear the existing data and create new tables."""
	init_db()
	click.echo('Initialized the database.')

# method to clean up post-response and add the db command
def init_app(app):
	app.teardown_appcontext(close_db)
	app.cli.add_command(init_db_command)

