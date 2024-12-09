import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Get table info
cursor.execute("PRAGMA table_info(tarefa)")
columns = cursor.fetchall()

print("Columns in tarefa table:")
for col in columns:
    print(col)

conn.close()
