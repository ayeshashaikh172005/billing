import os
import sqlite3
import io
from flask import Flask, redirect, url_for, session, render_template, request, flash, jsonify, g, send_file
from authlib.integrations.flask_client import OAuth
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- OAUTH SETUP ---
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# --- DATABASE SETUP ---
DATABASE = 'users.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE, timeout=30)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT UNIQUE, password TEXT, provider TEXT DEFAULT "local", picture TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)')
    cursor.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category_id INTEGER, price REAL, stock INTEGER, FOREIGN KEY (category_id) REFERENCES categories(id))')
    cursor.execute('CREATE TABLE IF NOT EXISTS invoices (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, total REAL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)')
    cursor.execute('CREATE TABLE IF NOT EXISTS invoice_items (id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_id INTEGER, product_id INTEGER, quantity INTEGER, price REAL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS staff (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, role TEXT, status TEXT DEFAULT "Active")')
    conn.commit()
    conn.close()

init_db()

# --- AUTH DECORATOR ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session: return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# --- ROUTES ---
@app.route('/')
def index():
    if 'user' in session: return redirect(url_for('dashboard'))
    return render_template('auth.html')

@app.route('/login')
def login():
    return google.authorize_redirect(url_for('google_auth', _external=True), prompt='select_account')

@app.route('/auth/google')
def google_auth():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        if user_info:
            db = get_db()
            with db:
                db.execute('INSERT OR IGNORE INTO users (email, name, provider, picture) VALUES (?, ?, ?, ?)', 
                           (user_info['email'], user_info['name'], 'google', user_info.get('picture')))
            session['user'] = {'name': user_info['name'], 'email': user_info['email'], 'picture': user_info.get('picture')}
            return redirect(url_for('dashboard'))
    except Exception as e: flash(f"Error: {str(e)}", "danger")
    return redirect(url_for('index'))

@app.route('/register', methods=['POST'])
def register_direct():
    data = request.json
    hashed_pw = generate_password_hash(data.get('password'))
    try:
        db = get_db()
        with db:
            db.execute('INSERT INTO users (email, name, password, provider) VALUES (?, ?, ?, ?)', 
                        (data.get('email'), data.get('name'), hashed_pw, 'local'))
        return jsonify({"message": "Success"}), 201
    except: return jsonify({"error": "Registration failed"}), 409

@app.route('/login-direct', methods=['POST'])
def login_direct():
    data = request.json
    db = get_db()
    user = db.execute('SELECT name, password FROM users WHERE email = ? AND provider = ?', (data.get('email'), 'local')).fetchone()
    if user and check_password_hash(user['password'], data.get('password')):
        session['user'] = {'name': user['name'], 'email': data.get('email')}
        return jsonify({"message": "Success"}), 200
    return jsonify({"error": "Invalid"}), 401

# --- ERP API ---
@app.route('/api/categories', methods=['GET', 'POST'])
@login_required
def categories_api():
    db = get_db()
    if request.method == 'POST':
        with db: db.execute("INSERT INTO categories (name) VALUES (?)", (request.json['name'],))
        return jsonify({"msg": "ok"}), 201
    return jsonify([dict(r) for r in db.execute("SELECT * FROM categories").fetchall()])

@app.route('/api/categories/<int:id>', methods=['PUT', 'DELETE'])
@login_required
def category_detail_api(id):
    db = get_db()
    if request.method == 'PUT':
        data = request.json
        with db: db.execute("UPDATE categories SET name = ? WHERE id = ?", (data['name'], id))
        return jsonify({"msg": "updated"})
    if request.method == 'DELETE':
        with db: db.execute("DELETE FROM categories WHERE id = ?", (id,))
        return jsonify({"success": True})

@app.route('/api/products', methods=['GET', 'POST'])
@login_required
def products_api():
    db = get_db()
    if request.method == 'POST':
        data = request.json
        with db: db.execute("INSERT INTO products (name, category_id, price, stock) VALUES (?, ?, ?, ?)", 
                          (data['name'], data['category_id'], data['price'], data['stock']))
        return jsonify({"msg": "ok"}), 201
    rows = db.execute('SELECT p.*, c.name as category_name FROM products p JOIN categories c ON p.category_id = c.id').fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/products/<int:id>', methods=['PUT', 'DELETE'])
@login_required
def product_detail_api(id):
    db = get_db()
    if request.method == 'PUT':
        data = request.json
        with db: db.execute("UPDATE products SET name = ?, category_id = ?, price = ?, stock = ? WHERE id = ?", 
                          (data['name'], data['category_id'], data['price'], data['stock'], id))
        return jsonify({"msg": "updated"})
    if request.method == 'DELETE':
        with db: db.execute("DELETE FROM products WHERE id = ?", (id,))
        return jsonify({"success": True})

@app.route('/api/staff', methods=['GET', 'POST'])
@login_required
def staff_api():
    db = get_db()
    if request.method == 'POST':
        with db: db.execute("INSERT INTO staff (name, role) VALUES (?, ?)", (request.json['name'], request.json['role']))
        return jsonify({"msg": "ok"}), 201
    return jsonify([dict(r) for r in db.execute("SELECT * FROM staff").fetchall()])

@app.route('/api/staff/<int:id>', methods=['PUT', 'DELETE'])
@login_required
def staff_detail_api(id):
    db = get_db()
    if request.method == 'PUT':
        data = request.json
        with db: db.execute("UPDATE staff SET name = ?, role = ? WHERE id = ?", (data['name'], data['role'], id))
        return jsonify({"msg": "updated"})
    if request.method == 'DELETE':
        with db: db.execute("DELETE FROM staff WHERE id = ?", (id,))
        return jsonify({"success": True})

@app.route('/api/invoices', methods=['GET', 'POST'])
@login_required
def invoices_api():
    db = get_db()
    if request.method == 'POST':
        data = request.json
        with db:
            cur = db.execute("INSERT INTO invoices (customer_name, total) VALUES (?, ?)", (data['customer_name'], data['total']))
            inv_id = cur.lastrowid
            for item in data['items']:
                db.execute("INSERT INTO invoice_items (invoice_id, product_id, quantity, price) VALUES (?, ?, ?, ?)", (inv_id, item['id'], item['qty'], item['price']))
                db.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (item['qty'], item['id']))
        return jsonify({"invoice_id": inv_id}), 201
    return jsonify([dict(r) for r in db.execute("SELECT * FROM invoices ORDER BY created_at DESC").fetchall()])

@app.route('/api/invoices/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def invoice_detail_api(id):
    db = get_db()
    if request.method == 'PUT':
        data = request.json
        with db: db.execute("UPDATE invoices SET customer_name = ? WHERE id = ?", (data['customer_name'], id))
        return jsonify({"msg": "updated"})
    if request.method == 'DELETE':
        with db:
            db.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (id,))
            db.execute("DELETE FROM invoices WHERE id = ?", (id,))
        return jsonify({"success": True})
    
    inv = db.execute("SELECT * FROM invoices WHERE id = ?", (id,)).fetchone()
    items = db.execute('''SELECT ii.*, p.name FROM invoice_items ii 
                          JOIN products p ON ii.product_id = p.id 
                          WHERE ii.invoice_id = ?''', (id,)).fetchall()
    return jsonify({"invoice": dict(inv), "items": [dict(i) for i in items]})

@app.route('/api/invoices/<int:invoice_id>/pdf')
@login_required
def generate_invoice_pdf(invoice_id):
    db = get_db()
    invoice = db.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
    items = db.execute("""
        SELECT ii.quantity, ii.price, p.name
        FROM invoice_items ii
        JOIN products p ON ii.product_id = p.id
        WHERE ii.invoice_id = ?
    """, (invoice_id,)).fetchall()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph(f"<b>Invoice #:</b> {invoice_id}", styles["Title"]))
    elements.append(Paragraph(f"<b>Customer:</b> {invoice['customer_name']}", styles["Normal"]))
    
    table_data = [["Product", "Qty", "Price", "Amount"]]
    for item in items:
        table_data.append([item["name"], str(item["quantity"]), f"₹{item['price']}", f"₹{item['price']*item['quantity']}"])
    
    table = Table(table_data)
    table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke)]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"invoice_{invoice_id}.pdf", mimetype="application/pdf")

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists('templates'): os.makedirs('templates')
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug=True, port=5000)
