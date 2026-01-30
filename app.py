from flask import Flask, render_template, request, jsonify, redirect, url_for, session, make_response
import sqlite3
import io
import base64
import numpy as np
from datetime import datetime
from textblob import TextBlob
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from deepface import DeepFace
import cv2
try:
    import nltk
    nltk.download('punkt', quiet=True)
    nltk.download('brown', quiet=True)
except Exception:
    pass

app = Flask(__name__)
app.secret_key = 'mdds_ultra_secure_key_2025'
DB_PATH = 'mdds.db'

# ---------------- DATABASE INITIALIZATION ----------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password_hash TEXT,
        name TEXT,
        created_at TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dish_name TEXT,
        category TEXT,
        mood_tag TEXT,
        price REAL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        dish_id INTEGER,
        mood_detected TEXT,
        status TEXT DEFAULT 'confirmed',
        kitchen_status TEXT DEFAULT 'pending',
        timestamp TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS mood_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        mood TEXT,
        input_text TEXT,
        timestamp TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        content TEXT,
        sentiment_score REAL,
        sentiment_label TEXT,
        timestamp TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS bulk_estimates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        people INTEGER,
        meal_type TEXT,
        budget_range TEXT,
        event_mood TEXT,
        estimated_total REAL,
        timestamp TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )''')

    c.execute(
        'INSERT OR IGNORE INTO admin (username, password) VALUES (?, ?)',
        ('admin', 'admin123')
    )

    sample_menu = [
        ('Dark Chocolate Lava Cake', 'Dessert', 'happy', 199.0),
        ('Spicy Jalapeno Pizza', 'Main Course', 'excited', 450.0),
        ('Warm Lentil Soup', 'Starter', 'sad', 150.0),
        ('Chamomile Herbal Tea', 'Beverage', 'stressed', 99.0),
        ('Classic Grilled Cheese', 'Main Course', 'neutral', 250.0)
    ]

    c.executemany(
        'INSERT OR IGNORE INTO menu (dish_name, category, mood_tag, price) VALUES (?, ?, ?, ?)',
        sample_menu
    )

    conn.commit()
    conn.close()

# ---------------- HELPERS ----------------
def get_db():
    return sqlite3.connect(DB_PATH)

# Mood to Food Category Mapping
MOOD_TO_FOOD_TAGS = {
    'happy': ['light', 'grilled', 'fresh', 'healthy', 'variety'],
    'sad': ['comfort', 'sweet', 'warm', 'creamy', 'rich'],
    'angry': ['spicy', 'crunchy', 'street', 'bold', 'tangy'],
    'stressed': ['light', 'low-oil', 'warm', 'calming', 'simple'],
    'tired': ['protein', 'energy', 'warm', 'simple', 'filling'],
    'excited': ['spicy', 'bold', 'variety', 'fresh', 'fusion'],
    'neutral': ['popular', 'combo', 'bestseller', 'classic', 'balanced']
}

# Mood descriptions for user
MOOD_MESSAGES = {
    'happy': "Based on your positive mood, we recommend fresh and light options that match your energy!",
    'sad': "We understand you need comfort. Here are warm and sweet dishes to lift your spirits.",
    'angry': "Feeling intense? Try these bold and spicy flavors to match your energy.",
    'stressed': "You need something calming. Here are light and soothing options for you.",
    'tired': "Low on energy? These protein-rich meals will help restore your strength.",
    'excited': "Your excitement deserves bold flavors! Check out these vibrant dishes.",
    'neutral': "Here are our most popular and well-balanced dishes for you."
}

def get_food_recommendations(mood):
    """Get personalized food recommendations based on detected mood with ranking"""
    conn = get_db()
    
    # Get all menu items
    all_items = conn.execute('SELECT * FROM menu').fetchall()
    
    # Score each item based on mood match
    scored_items = []
    
    for item in all_items:
        item_id, dish_name, category, mood_tag, price = item[:5]
        score = 0
        
        # 1. Exact mood match (50% weight)
        if mood_tag == mood:
            score += 5
        
        # 2. Category preference (30% weight)
        category_map = {
            'happy': ['Dessert', 'Main Course', 'Starter'],
            'sad': ['Dessert', 'Beverage', 'Main Course'],
            'angry': ['Main Course', 'Starter'],
            'stressed': ['Beverage', 'Starter', 'Main Course'],
            'tired': ['Main Course', 'Beverage'],
            'excited': ['Main Course', 'Starter', 'Dessert'],
            'neutral': ['Main Course', 'Starter', 'Dessert']
        }
        
        preferred_categories = category_map.get(mood, [])
        if category in preferred_categories:
            score += 3 - preferred_categories.index(category)  # Higher score for first preference
        
        # 3. Keyword matching in dish name (20% weight)
        dish_lower = dish_name.lower()
        food_tags = MOOD_TO_FOOD_TAGS.get(mood, [])
        for tag in food_tags:
            if tag in dish_lower:
                score += 2
        
        scored_items.append((score, item))
    
    # Sort by score (descending) and get top 5
    scored_items.sort(reverse=True, key=lambda x: x[0])
    recommendations = [item for score, item in scored_items[:5]]
    
    conn.close()
    return recommendations

def analyze_sentiment(text):
    import re
    
    # Mood keyword lexicon
    MOOD_KEYWORDS = {
        'happy': ['happy', 'good', 'great', 'excited', 'awesome', 'fresh', 'positive', 'wonderful', 'excellent', 'joyful', 'pleased', 'glad', 'cheerful'],
        'sad': ['sad', 'low', 'down', 'empty', 'lonely', 'depressed', 'heavy', 'unhappy', 'disappointed', 'upset', 'dull', 'missing'],
        'angry': ['angry', 'irritated', 'annoyed', 'frustrated', 'mad', 'furious', 'rage', 'temper'],
        'stressed': ['stressed', 'pressure', 'overwhelmed', 'tension', 'anxious', 'mentally', 'busy', 'worried', 'restless'],
        'tired': ['tired', 'exhausted', 'sleepy', 'fatigued', 'drained', 'weary'],
        'excited': ['excited', 'thrilled', 'energetic', 'pumped', 'enthusiastic', 'amazing', 'fantastic']
    }
    
    # Preprocess text
    text_lower = text.lower()
    text_lower = re.sub(r'[^\w\s]', '', text_lower)
    tokens = text_lower.split()
    
    # Score each mood
    mood_scores = {mood: 0 for mood in MOOD_KEYWORDS.keys()}
    
    for token in tokens:
        for mood, keywords in MOOD_KEYWORDS.items():
            if token in keywords:
                mood_scores[mood] += 1
    
    # Get sentiment polarity
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    
    # Adjust scores with polarity
    if polarity > 0.3:
        mood_scores['happy'] += 1
        mood_scores['excited'] += 0.5
    elif polarity < -0.3:
        mood_scores['sad'] += 1
        mood_scores['stressed'] += 0.5
    
    # Find highest scoring mood
    max_mood = max(mood_scores, key=mood_scores.get)
    max_score = mood_scores[max_mood]
    
    # If no clear mood detected, return neutral
    if max_score < 1:
        return 'neutral', polarity
    
    # Map tired and angry to stressed for food recommendations
    mood_map = {
        'tired': 'stressed',
        'angry': 'stressed'
    }
    
    final_mood = mood_map.get(max_mood, max_mood)
    return final_mood, polarity

def analyze_face_emotion(image_data):
    try:
        if not image_data or ',' not in image_data:
            print("Invalid image data format")
            return 'neutral', 'error'
        
        img_bytes = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            print("Failed to decode image")
            return 'neutral', 'error'
        
        print(f"Analyzing image of shape: {img.shape}")
        result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
        print(f"DeepFace result: {result}")
        
        emotion = result[0]['dominant_emotion']
        print(f"Detected emotion: {emotion}")
        
        mood_map = {
            'happy': 'happy',
            'sad': 'sad',
            'angry': 'stressed',
            'fear': 'stressed',
            'surprise': 'excited',
            'neutral': 'neutral',
            'disgust': 'sad'
        }
        mapped_mood = mood_map.get(emotion, 'neutral')
        print(f"Mapped mood: {mapped_mood}")
        return mapped_mood, emotion
    except Exception as e:
        print(f"Face analysis error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return 'neutral', 'error'

# ---------------- AUTH ROUTES ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed = generate_password_hash(request.form['password'])
        try:
            conn = get_db()
            conn.execute(
                'INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)',
                (request.form['name'], request.form['email'], hashed, datetime.now().isoformat())
            )
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Email already exists", 400
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = get_db()
        user = conn.execute(
            'SELECT * FROM users WHERE email=?', (request.form['email'],)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user[2], request.form['password']):
            session['user_id'] = user[0]
            session['user_name'] = user[3]
            return redirect(url_for('mood_analysis'))
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/')
def index():
    return render_template('landing.html', user_name=session.get('user_name', 'Guest'))

@app.route('/test')
def test():
    return "<h1>Test Route Works!</h1>"

@app.route('/home')
def home():
    return render_template('index.html', user_name=session.get('user_name', 'Guest'))

@app.route('/mood-analysis')
def mood_analysis():
    return render_template('index.html', user_name=session.get('user_name', 'Guest'))

# ---------------- MDDS CORE ----------------
@app.route('/detect_mood', methods=['POST'])
def detect_mood():
    text = request.json.get('text', '')
    mood, polarity = analyze_sentiment(text)

    if 'user_id' in session:
        conn = get_db()
        conn.execute(
            'INSERT INTO mood_history (user_id, mood, input_text, timestamp) VALUES (?, ?, ?, ?)',
            (session['user_id'], mood, text, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    
    recs = get_food_recommendations(mood)

    return jsonify({
        'mood': mood, 
        'recommendations': recs,
        'food_tags': MOOD_TO_FOOD_TAGS.get(mood, []),
        'mood_message': MOOD_MESSAGES.get(mood, ''),
        'confidence': abs(polarity)
    })

@app.route('/detect_mood_face', methods=['POST'])
def detect_mood_face():
    image_data = request.json.get('image', '')
    mood, emotion = analyze_face_emotion(image_data)

    if 'user_id' in session:
        conn = get_db()
        conn.execute(
            'INSERT INTO mood_history (user_id, mood, input_text, timestamp) VALUES (?, ?, ?, ?)',
            (session['user_id'], mood, f'Face: {emotion}', datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    
    recs = get_food_recommendations(mood)

    return jsonify({
        'mood': mood, 
        'emotion': emotion, 
        'recommendations': recs,
        'food_tags': MOOD_TO_FOOD_TAGS.get(mood, []),
        'mood_message': MOOD_MESSAGES.get(mood, '')
    })

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login to place order', 'redirect': '/login'}), 401

    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO orders (user_id, dish_id, mood_detected, timestamp) VALUES (?, ?, ?, ?)',
        (session['user_id'], data['dish_id'], data['mood'], datetime.now().isoformat())
    )
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'order_id': order_id})

# ---------------- AI RECEIPT ----------------
@app.route('/generate_ai_receipt/<int:order_id>')
def generate_ai_receipt(order_id):
    conn = get_db()
    order = conn.execute('''
        SELECT o.id, m.dish_name, m.price, o.mood_detected, u.name
        FROM orders o
        JOIN menu m ON o.dish_id = m.id
        JOIN users u ON o.user_id = u.id
        WHERE o.id = ?
    ''', (order_id,)).fetchone()
    conn.close()

    if not order:
        return "Order not found", 404

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(100, 750, "MDDS – AI DIGITAL RECEIPT")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 710, f"Customer: {order[4]}")
    pdf.drawString(100, 690, f"Dish: {order[1]}")
    pdf.drawString(100, 670, f"Price: ₹{order[2]}")
    pdf.drawString(100, 650, f"Mood Detected: {order[3].upper()}")
    pdf.drawString(100, 620, "AI Insight: This meal matches your emotional state perfectly!")
    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    return response

# ---------------- ADMIN ----------------
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db()
    moods = conn.execute('SELECT mood, COUNT(*) FROM mood_history GROUP BY mood').fetchall()
    feedback = conn.execute('SELECT sentiment_label, COUNT(*) FROM feedback GROUP BY sentiment_label').fetchall()
    orders = conn.execute('''SELECT o.id, u.name, m.dish_name, o.mood_detected, o.status, o.timestamp 
                             FROM orders o JOIN users u ON o.user_id = u.id 
                             JOIN menu m ON o.dish_id = m.id ORDER BY o.timestamp DESC LIMIT 10''').fetchall()
    kitchen_orders = conn.execute('''SELECT o.id, u.name, m.dish_name, o.mood_detected, o.timestamp, o.kitchen_status 
                             FROM orders o JOIN users u ON o.user_id = u.id 
                             JOIN menu m ON o.dish_id = m.id 
                             WHERE o.kitchen_status != 'completed'
                             ORDER BY o.timestamp ASC''').fetchall()
    menu = conn.execute('SELECT * FROM menu ORDER BY category').fetchall()
    total_revenue = conn.execute('SELECT SUM(m.price) FROM orders o JOIN menu m ON o.dish_id = m.id').fetchone()[0] or 0
    total_orders = conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
    total_customers = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    conn.close()

    return render_template('admin_dashboard.html', mood_stats=moods, feedback_stats=feedback,
                          orders=orders, kitchen_orders=kitchen_orders, menu=menu, total_revenue=total_revenue, 
                          total_orders=total_orders, total_customers=total_customers)

@app.route('/admin/add_menu', methods=['POST'])
def add_menu():
    if 'admin' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    conn = get_db()
    conn.execute('INSERT INTO menu (dish_name, category, mood_tag, price, image) VALUES (?, ?, ?, ?, ?)',
                (data['dish_name'], data['category'], data['mood_tag'], data['price'], data.get('image', '')))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/admin/delete_menu/<int:id>', methods=['DELETE'])
def delete_menu(id):
    if 'admin' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    conn.execute('DELETE FROM menu WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/kitchen')
def kitchen_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db()
    orders = conn.execute('''SELECT o.id, u.name, m.dish_name, o.mood_detected, o.timestamp, o.kitchen_status 
                             FROM orders o JOIN users u ON o.user_id = u.id 
                             JOIN menu m ON o.dish_id = m.id 
                             WHERE o.kitchen_status != 'completed'
                             ORDER BY o.timestamp ASC''').fetchall()
    conn.close()
    return render_template('kitchen_dashboard.html', orders=orders)

@app.route('/update_kitchen_status', methods=['POST'])
def update_kitchen_status():
    if 'admin' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    conn = get_db()
    conn.execute('UPDATE orders SET kitchen_status = ? WHERE id = ?', 
                (data['status'], data['order_id']))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------------- BULK ORDER ESTIMATOR ----------------
@app.route('/bulk-estimator')
def bulk_estimator():
    return render_template('bulk_estimator.html', user_name=session.get('user_name', 'Guest'))

@app.route('/calculate_bulk_estimate', methods=['POST'])
def calculate_bulk_estimate():
    try:
        data = request.json
        people = int(data.get('people', 0))
        meal_type = data.get('meal_type', 'lunch')
        budget_range = data.get('budget_range', 'standard')
        event_mood = data.get('event_mood', 'neutral')
        
        # Dynamic pricing by meal type
        meal_prices = {'breakfast': 150, 'lunch': 250, 'dinner': 350, 'snacks': 100}
        base_price = meal_prices.get(meal_type, 250)
        
        # Budget range multiplier
        budget_multipliers = {'economy': 0.7, 'standard': 1.0, 'premium': 1.5}
        multiplier = budget_multipliers.get(budget_range, 1.0)
        
        # Calculate base total
        avg_price = base_price * multiplier
        subtotal = people * avg_price
        
        # Group discount
        discount = 0
        if people > 100:
            discount = 0.15
        elif people > 50:
            discount = 0.10
        
        discount_amount = subtotal * discount
        after_discount = subtotal - discount_amount
        
        # Taxes and charges
        gst = after_discount * 0.05
        service_charge = after_discount * 0.08
        buffer = after_discount * 0.05
        grand_total = after_discount + gst + service_charge + buffer
        
        # Get category-wise menu suggestions based on mood
        conn = get_db()
        
        # Mood-based category preferences
        mood_categories = {
            'happy': ['Dessert', 'Main Course', 'Beverage'],
            'stressed': ['Beverage', 'Starter', 'Dessert'],
            'excited': ['Main Course', 'Starter', 'Dessert'],
            'neutral': ['Main Course', 'Starter', 'Beverage']
        }
        
        categories = mood_categories.get(event_mood, ['Main Course', 'Starter', 'Dessert'])
        menu_suggestions = {}
        
        for category in categories:
            items = conn.execute(
                'SELECT dish_name, price, mood_tag FROM menu WHERE category=? LIMIT 3',
                (category,)
            ).fetchall()
            menu_suggestions[category] = [{'name': i[0], 'price': i[1], 'mood': i[2]} for i in items]
        
        conn.close()
        
        # Store estimation request (only if user is logged in)
        if 'user_id' in session:
            try:
                conn = get_db()
                conn.execute(
                    'INSERT INTO bulk_estimates (user_id, people, meal_type, budget_range, event_mood, estimated_total, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (session['user_id'], people, meal_type, budget_range, event_mood, grand_total, datetime.now().isoformat())
                )
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Error storing estimate: {e}")
        
        return jsonify({
            'people': people,
            'meal_type': meal_type,
            'budget_range': budget_range,
            'event_mood': event_mood,
            'avg_price_per_person': round(avg_price, 2),
            'subtotal': round(subtotal, 2),
            'discount_percent': discount * 100,
            'discount_amount': round(discount_amount, 2),
            'after_discount': round(after_discount, 2),
            'gst': round(gst, 2),
            'service_charge': round(service_charge, 2),
            'buffer': round(buffer, 2),
            'grand_total': round(grand_total, 2),
            'menu_suggestions': menu_suggestions
        })
    except Exception as e:
        print(f"Bulk estimate error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/generate_bulk_quotation', methods=['POST'])
def generate_bulk_quotation():
    data = request.json
    
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    
    # Header
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(100, 750, "MDDS - Bulk Order Quotation")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(100, 735, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Event Details
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(100, 700, "Event Details")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(100, 680, f"Number of People: {data['people']}")
    pdf.drawString(100, 665, f"Meal Type: {data['meal_type'].title()}")
    pdf.drawString(100, 650, f"Budget Range: {data['budget_range'].title()}")
    pdf.drawString(100, 635, f"Event Mood: {data['event_mood'].title()}")
    
    # Cost Breakdown
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(100, 605, "Cost Breakdown")
    pdf.setFont("Helvetica", 11)
    y = 585
    pdf.drawString(100, y, f"Avg Price/Person: ₹{data['avg_price_per_person']}"); y -= 20
    pdf.drawString(100, y, f"Subtotal: ₹{data['subtotal']}"); y -= 20
    if data['discount_percent'] > 0:
        pdf.drawString(100, y, f"Group Discount ({data['discount_percent']}%): -₹{data['discount_amount']}"); y -= 20
        pdf.drawString(100, y, f"After Discount: ₹{data['after_discount']}"); y -= 20
    pdf.drawString(100, y, f"GST (5%): ₹{data['gst']}"); y -= 20
    pdf.drawString(100, y, f"Service Charge (8%): ₹{data['service_charge']}"); y -= 20
    pdf.drawString(100, y, f"Buffer (5%): ₹{data['buffer']}"); y -= 25
    
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(100, y, f"Grand Total: ₹{data['grand_total']}"); y -= 30
    
    # Menu Suggestions
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(100, y, "Recommended Menu"); y -= 20
    pdf.setFont("Helvetica", 10)
    
    for category, items in data.get('menu_suggestions', {}).items():
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(100, y, f"{category}:"); y -= 15
        pdf.setFont("Helvetica", 10)
        for item in items:
            pdf.drawString(120, y, f"• {item['name']} - ₹{item['price']}"); y -= 15
        y -= 5
    
    pdf.showPage()
    pdf.save()
    
    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=bulk_quotation.pdf'
    return response

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
