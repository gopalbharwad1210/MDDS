import sqlite3

conn = sqlite3.connect('mdds.db')
c = conn.cursor()

# Update all items with placeholder images
c.execute('''UPDATE menu SET image = 
    'https://via.placeholder.com/300x200/FF6B6B/FFFFFF?text=' || 
    REPLACE(REPLACE(dish_name, ' ', '+'), '&', 'and')
''')

conn.commit()
print(f"Updated {c.rowcount} items with placeholder images")
conn.close()
