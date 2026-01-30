import sqlite3

conn = sqlite3.connect('mdds.db')
c = conn.cursor()

# Clear existing menu
c.execute('DELETE FROM menu')
print("Cleared existing menu items")

# Grand Comfort Hotel - 150 Items
menu_items = [
    # SOUPS (1-10)
    ('Tomato Basil Soup', 'Soup', 'stressed', 120.0, 'light,warm,calming'),
    ('Sweet Corn Vegetable Soup', 'Soup', 'sad', 110.0, 'light,comfort'),
    ('Hot & Sour Soup', 'Soup', 'angry', 130.0, 'spicy,energy'),
    ('Manchow Soup', 'Soup', 'angry', 140.0, 'spicy,energy'),
    ('Cream of Mushroom Soup', 'Soup', 'sad', 150.0, 'creamy,comfort'),
    ('Lemon Coriander Soup', 'Soup', 'stressed', 120.0, 'light,fresh,calming'),
    ('Chicken Clear Soup', 'Soup', 'tired', 140.0, 'protein,light'),
    ('Chicken Sweet Corn Soup', 'Soup', 'tired', 150.0, 'protein,comfort'),
    ('Chicken Hot & Sour Soup', 'Soup', 'angry', 160.0, 'spicy,energy'),
    ('Cream of Chicken Soup', 'Soup', 'sad', 170.0, 'creamy,comfort'),
    
    # SALADS (11-20)
    ('Green Salad', 'Salad', 'happy', 100.0, 'fresh,light'),
    ('Russian Salad', 'Salad', 'sad', 130.0, 'creamy,comfort'),
    ('Caesar Salad (Veg)', 'Salad', 'happy', 150.0, 'fresh,light'),
    ('Caesar Salad (Chicken)', 'Salad', 'happy', 180.0, 'protein'),
    ('Sprouts Salad', 'Salad', 'stressed', 120.0, 'protein,light'),
    ('Fruit Salad', 'Salad', 'happy', 140.0, 'fresh,sweet'),
    ('Pasta Salad', 'Salad', 'neutral', 160.0, 'comfort'),
    ('Coleslaw', 'Salad', 'sad', 110.0, 'creamy,comfort'),
    ('Chickpea Salad', 'Salad', 'tired', 130.0, 'protein'),
    ('Grilled Vegetable Salad', 'Salad', 'happy', 150.0, 'fresh'),
    
    # VEG STARTERS (21-35)
    ('Paneer Tikka', 'Starter', 'happy', 220.0, 'grilled,protein'),
    ('Paneer Malai Tikka', 'Starter', 'sad', 240.0, 'creamy,comfort'),
    ('Paneer Pakora', 'Starter', 'sad', 180.0, 'fried,comfort'),
    ('Veg Manchurian', 'Starter', 'angry', 200.0, 'spicy'),
    ('Gobi Manchurian', 'Starter', 'angry', 190.0, 'spicy'),
    ('Crispy Corn', 'Starter', 'happy', 170.0, 'crunchy,comfort'),
    ('Veg Spring Roll', 'Starter', 'happy', 180.0, 'crunchy'),
    ('Hara Bhara Kebab', 'Starter', 'happy', 200.0, 'light,healthy'),
    ('Cheese Balls', 'Starter', 'sad', 190.0, 'comfort'),
    ('Stuffed Mushroom', 'Starter', 'neutral', 210.0, 'comfort'),
    ('Chilli Paneer', 'Starter', 'angry', 230.0, 'spicy'),
    ('Corn Cheese Croquettes', 'Starter', 'happy', 200.0, 'comfort'),
    ('Veg Seekh Kebab', 'Starter', 'happy', 210.0, 'protein'),
    ('Aloo Tikki', 'Starter', 'sad', 150.0, 'comfort'),
    ('Cheese Garlic Bread', 'Starter', 'happy', 160.0, 'comfort'),
    
    # NON-VEG STARTERS (36-50)
    ('Chicken Tikka', 'Starter', 'happy', 280.0, 'protein'),
    ('Chicken Malai Tikka', 'Starter', 'sad', 300.0, 'creamy,comfort'),
    ('Chicken Seekh Kebab', 'Starter', 'tired', 290.0, 'protein,energy'),
    ('Chicken 65', 'Starter', 'angry', 270.0, 'spicy'),
    ('Chilli Chicken', 'Starter', 'angry', 280.0, 'spicy'),
    ('Chicken Lollipop', 'Starter', 'happy', 290.0, 'crunchy'),
    ('Fish Finger', 'Starter', 'happy', 320.0, 'crunchy'),
    ('Fish Tikka', 'Starter', 'happy', 340.0, 'protein'),
    ('Prawn Tempura', 'Starter', 'happy', 380.0, 'crunchy'),
    ('Mutton Seekh Kebab', 'Starter', 'tired', 350.0, 'protein,energy'),
    ('Mutton Shami Kebab', 'Starter', 'sad', 340.0, 'comfort'),
    ('Tandoori Chicken (Half)', 'Starter', 'happy', 320.0, 'protein'),
    ('Tandoori Chicken (Full)', 'Starter', 'tired', 580.0, 'protein,energy'),
    ('Butter Garlic Prawns', 'Starter', 'happy', 420.0, 'comfort'),
    ('Pepper Chicken', 'Starter', 'angry', 290.0, 'spicy'),
    
    # VEG MAIN COURSE (51-70)
    ('Paneer Butter Masala', 'Main Course', 'sad', 280.0, 'creamy,comfort'),
    ('Paneer Tikka Masala', 'Main Course', 'happy', 290.0, 'protein'),
    ('Shahi Paneer', 'Main Course', 'sad', 300.0, 'rich,comfort'),
    ('Kadai Paneer', 'Main Course', 'angry', 280.0, 'spicy'),
    ('Palak Paneer', 'Main Course', 'stressed', 270.0, 'light'),
    ('Matar Paneer', 'Main Course', 'neutral', 250.0, 'comfort'),
    ('Dal Fry', 'Main Course', 'stressed', 180.0, 'light'),
    ('Dal Tadka', 'Main Course', 'neutral', 190.0, 'comfort'),
    ('Dal Makhani', 'Main Course', 'sad', 220.0, 'creamy,comfort'),
    ('Chole Masala', 'Main Course', 'tired', 200.0, 'energy'),
    ('Rajma Masala', 'Main Course', 'tired', 210.0, 'comfort'),
    ('Mix Vegetable Curry', 'Main Course', 'stressed', 230.0, 'light'),
    ('Veg Kolhapuri', 'Main Course', 'angry', 260.0, 'spicy'),
    ('Malai Kofta', 'Main Course', 'sad', 280.0, 'rich,comfort'),
    ('Dum Aloo', 'Main Course', 'neutral', 240.0, 'comfort'),
    ('Aloo Gobi', 'Main Course', 'neutral', 220.0, 'light'),
    ('Bhindi Masala', 'Main Course', 'stressed', 230.0, 'light'),
    ('Veg Handi', 'Main Course', 'neutral', 270.0, 'comfort'),
    ('Vegetable Khichdi', 'Main Course', 'stressed', 180.0, 'calming'),
    ('Veg Curry (Home Style)', 'Main Course', 'neutral', 220.0, 'comfort'),
    
    # NON-VEG MAIN COURSE (71-90)
    ('Butter Chicken', 'Main Course', 'sad', 350.0, 'creamy,comfort'),
    ('Chicken Tikka Masala', 'Main Course', 'happy', 340.0, 'protein'),
    ('Chicken Curry (Home Style)', 'Main Course', 'tired', 320.0, 'comfort'),
    ('Kadai Chicken', 'Main Course', 'angry', 330.0, 'spicy'),
    ('Chicken Kolhapuri', 'Main Course', 'angry', 340.0, 'spicy'),
    ('Chicken Handi', 'Main Course', 'neutral', 350.0, 'comfort'),
    ('Mutton Curry', 'Main Course', 'tired', 420.0, 'energy'),
    ('Mutton Rogan Josh', 'Main Course', 'sad', 450.0, 'rich,comfort'),
    ('Mutton Handi', 'Main Course', 'neutral', 440.0, 'comfort'),
    ('Egg Curry', 'Main Course', 'tired', 200.0, 'protein'),
    ('Egg Masala', 'Main Course', 'tired', 210.0, 'protein,energy'),
    ('Fish Curry', 'Main Course', 'stressed', 380.0, 'light'),
    ('Fish Masala', 'Main Course', 'angry', 390.0, 'spicy'),
    ('Prawn Masala', 'Main Course', 'happy', 480.0, 'rich'),
    ('Prawn Curry', 'Main Course', 'happy', 470.0, 'comfort'),
    ('Chicken Saagwala', 'Main Course', 'stressed', 330.0, 'light'),
    ('Chicken Do Pyaza', 'Main Course', 'happy', 340.0, 'neutral'),
    ('Mutton Keema', 'Main Course', 'tired', 400.0, 'protein,energy'),
    ('Keema Mutter', 'Main Course', 'tired', 410.0, 'protein'),
    ('Chicken Stew', 'Main Course', 'stressed', 320.0, 'calming'),
    
    # RICE ITEMS (91-100)
    ('Steamed Rice', 'Rice', 'stressed', 120.0, 'light,neutral'),
    ('Jeera Rice', 'Rice', 'stressed', 140.0, 'light,comfort'),
    ('Veg Pulao', 'Rice', 'neutral', 180.0, 'mild,comfort'),
    ('Kashmiri Pulao', 'Rice', 'happy', 200.0, 'sweet,comfort'),
    ('Chicken Fried Rice', 'Rice', 'tired', 220.0, 'energy'),
    ('Veg Fried Rice', 'Rice', 'neutral', 190.0, 'energy'),
    ('Egg Fried Rice', 'Rice', 'tired', 200.0, 'protein,energy'),
    ('Chicken Biryani', 'Rice', 'angry', 280.0, 'spicy,energy'),
    ('Veg Biryani', 'Rice', 'happy', 240.0, 'comfort'),
    ('Mutton Biryani', 'Rice', 'angry', 350.0, 'rich,energy'),
    
    # INDIAN BREADS (101-110)
    ('Plain Roti', 'Bread', 'stressed', 30.0, 'light,neutral'),
    ('Butter Roti', 'Bread', 'neutral', 40.0, 'comfort'),
    ('Tandoori Roti', 'Bread', 'neutral', 35.0, 'light'),
    ('Butter Naan', 'Bread', 'sad', 50.0, 'comfort'),
    ('Garlic Naan', 'Bread', 'happy', 60.0, 'comfort'),
    ('Cheese Naan', 'Bread', 'sad', 80.0, 'rich,comfort'),
    ('Laccha Paratha', 'Bread', 'happy', 55.0, 'comfort'),
    ('Missi Roti', 'Bread', 'neutral', 45.0, 'light'),
    ('Roomali Roti', 'Bread', 'neutral', 40.0, 'light'),
    ('Stuffed Kulcha', 'Bread', 'happy', 70.0, 'comfort'),
    
    # QUICK BITES (111-120)
    ('Veg Burger', 'Quick Bites', 'happy', 150.0, 'comfort'),
    ('Chicken Burger', 'Quick Bites', 'happy', 180.0, 'protein,energy'),
    ('Veg Sandwich', 'Quick Bites', 'neutral', 120.0, 'light'),
    ('Chicken Sandwich', 'Quick Bites', 'tired', 150.0, 'protein'),
    ('French Fries', 'Quick Bites', 'happy', 100.0, 'crunchy,comfort'),
    ('Cheese Fries', 'Quick Bites', 'sad', 130.0, 'comfort'),
    ('Veg Pizza', 'Quick Bites', 'happy', 250.0, 'comfort'),
    ('Chicken Pizza', 'Quick Bites', 'happy', 300.0, 'protein,energy'),
    ('Pav Bhaji', 'Quick Bites', 'angry', 140.0, 'spicy,comfort'),
    ('Vada Pav', 'Quick Bites', 'angry', 80.0, 'spicy,comfort'),
    
    # DESSERTS (121-130)
    ('Gulab Jamun', 'Dessert', 'sad', 80.0, 'sweet,comfort'),
    ('Rasgulla', 'Dessert', 'happy', 90.0, 'sweet,comfort'),
    ('Ice Cream (Vanilla)', 'Dessert', 'sad', 100.0, 'sweet,calming'),
    ('Ice Cream (Chocolate)', 'Dessert', 'happy', 110.0, 'sweet,comfort'),
    ('Brownie with Ice Cream', 'Dessert', 'sad', 180.0, 'sweet,comfort'),
    ('Fruit Custard', 'Dessert', 'happy', 120.0, 'sweet,calming'),
    ('Shrikhand', 'Dessert', 'happy', 100.0, 'sweet,comfort'),
    ('Gajar Halwa', 'Dessert', 'sad', 110.0, 'warm,sweet'),
    ('Cheesecake', 'Dessert', 'happy', 200.0, 'sweet,rich'),
    ('Chocolate Mousse', 'Dessert', 'happy', 180.0, 'sweet,comfort'),
    
    # BEVERAGES (131-140)
    ('Mineral Water', 'Beverage', 'neutral', 20.0, 'neutral'),
    ('Fresh Lime Soda', 'Beverage', 'happy', 60.0, 'refreshing'),
    ('Cold Coffee', 'Beverage', 'tired', 100.0, 'energy'),
    ('Hot Coffee', 'Beverage', 'tired', 80.0, 'energy'),
    ('Masala Tea', 'Beverage', 'stressed', 50.0, 'warm,calming'),
    ('Green Tea', 'Beverage', 'stressed', 60.0, 'calming'),
    ('Fresh Fruit Juice', 'Beverage', 'happy', 90.0, 'fresh'),
    ('Milkshake (Vanilla)', 'Beverage', 'happy', 120.0, 'sweet,comfort'),
    ('Milkshake (Chocolate)', 'Beverage', 'sad', 130.0, 'sweet,comfort'),
    ('Soft Drinks', 'Beverage', 'neutral', 50.0, 'refreshing'),
    
    # MOCKTAILS (141-150)
    ('Blue Lagoon', 'Mocktail', 'happy', 150.0, 'refreshing'),
    ('Virgin Mojito', 'Mocktail', 'happy', 140.0, 'fresh,calming'),
    ('Strawberry Mocktail', 'Mocktail', 'happy', 160.0, 'sweet'),
    ('Mint Cooler', 'Mocktail', 'stressed', 130.0, 'calming'),
    ('Watermelon Cooler', 'Mocktail', 'happy', 140.0, 'fresh,calming'),
    ('Lemon Iced Tea', 'Mocktail', 'neutral', 100.0, 'refreshing'),
    ('Peach Iced Tea', 'Mocktail', 'happy', 110.0, 'refreshing'),
    ('Chocolate Shake', 'Mocktail', 'sad', 150.0, 'sweet,comfort'),
    ('Mango Smoothie', 'Mocktail', 'happy', 160.0, 'sweet,energy'),
    ('Banana Shake', 'Mocktail', 'tired', 140.0, 'energy')
]

# Insert all items
for item in menu_items:
    c.execute('INSERT INTO menu (dish_name, category, mood_tag, price, image) VALUES (?, ?, ?, ?, ?)', item)

conn.commit()
print(f"Added {len(menu_items)} menu items successfully!")
conn.close()
