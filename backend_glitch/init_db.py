import sqlite3

conn = sqlite3.connect('NumberPlate.db')
cur = conn.cursor()

# Create users table
cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    mobile TEXT,
    car_number TEXT UNIQUE,
    email TEXT,
    flat_number TEXT
)
''')

# Create detections table
cur.execute('''
CREATE TABLE IF NOT EXISTS detections (
    tid INTEGER PRIMARY KEY AUTOINCREMENT,
    car_number TEXT NOT NULL,
    timestamp TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print("Database, users table, and detections table created.")
