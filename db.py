import sqlite3

conn = sqlite3.connect("costeo.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE ingredientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    unidad TEXT,
    precio REAL,
    cantidad REAL,
    costo_unitario REAL
)
""")

conn.commit()
conn.close()

print("Base de datos creada")