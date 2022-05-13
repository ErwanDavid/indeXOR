import sqlite3

conn = sqlite3.connect('MyDataBase.db')
#conn = sqlite3.connect('file:../MyDataBase.db?mode=ro', uri=True)
QueryCurs = conn.cursor()
QueryCurs.execute("SELECT name FROM sqlite_master WHERE type = 'table'")