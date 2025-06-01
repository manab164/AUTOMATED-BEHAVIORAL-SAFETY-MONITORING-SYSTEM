import sqlite3

# Connect (or create) the database file
conn = sqlite3.connect("violationss2.db")
cursor = conn.cursor()

# Create the violations table with an image blob column
cursor.execute("""
CREATE TABLE IF NOT EXISTS violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    frame_number INTEGER,
    people_count INTEGER,
    timestamp REAL,
    violations TEXT,
    violation_count INTEGER,
    violation_image BLOB
    area TEXT
    
)
""")

conn.commit()
conn.close()

print("✅ Database and table created successfully!")
