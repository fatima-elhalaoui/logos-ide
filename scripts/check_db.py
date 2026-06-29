import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "logos_dict.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM words")
count = cursor.fetchone()[0]
with open('db_count.txt', 'w') as f:
    f.write(f"Words in database: {count}")
conn.close()
