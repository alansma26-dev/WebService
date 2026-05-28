import sqlite3

conn = sqlite3.connect("costeo.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS ingredientes (
    nombre TEXT PRIMARY KEY,
    unidad TEXT,
    precio REAL,
    cantidad REAL,
    costo_unitario REAL
)
""")

conn.commit()
conn.close()