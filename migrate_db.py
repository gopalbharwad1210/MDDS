import sqlite3

# Connect to database
conn = sqlite3.connect('mdds.db')
c = conn.cursor()

# Check if user_id column exists in orders table
try:
    c.execute("SELECT user_id FROM orders LIMIT 1")
    print("Database schema is correct")
except sqlite3.OperationalError:
    print("Fixing database schema...")
    
    # Drop old table and create new one
    c.execute('DROP TABLE IF EXISTS orders')
    c.execute('''CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        dish_id INTEGER,
        mood_detected TEXT,
        status TEXT DEFAULT 'confirmed',
        kitchen_status TEXT DEFAULT 'pending',
        timestamp TEXT
    )''')
    print("Database fixed successfully")

# Add image column to menu if not exists
try:
    c.execute("SELECT image FROM menu LIMIT 1")
except sqlite3.OperationalError:
    c.execute('ALTER TABLE menu ADD COLUMN image TEXT')
    print("Added image column to menu")

# Remove duplicate menu items
c.execute('''DELETE FROM menu WHERE id NOT IN 
             (SELECT MIN(id) FROM menu GROUP BY LOWER(dish_name))''')
removed = c.rowcount
if removed > 0:
    print(f"Removed {removed} duplicate menu items")

conn.commit()
conn.close()
print("Database ready!")
