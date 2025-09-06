from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import pymysql
import re
from functools import wraps
import joblib
import numpy as np
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'adhd',
    'charset': 'utf8mb4'
}

# Load model, scaler, and features
try:
    model = joblib.load('lr_model.pkl')
    scaler = joblib.load('scaler.pkl')
    features = joblib.load('features.pkl')
except FileNotFoundError as e:
    print(f"Error loading model files: {e}")
    model, scaler, features = None, None, []

def get_db_connection():
    try:
        return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as err:
        print(f"Database connection error: {err}")
        return None

def init_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                age INT,
                gender ENUM('Male', 'Female', 'Other', 'Non-binary', 'Prefer not to say') DEFAULT 'Other',
                phone VARCHAR(20),
                address TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """
        create_results_table = """
            CREATE TABLE IF NOT EXISTS results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                score INT NOT NULL,
                percentage DECIMAL(5,2) NOT NULL,
                message TEXT,
                risk_level ENUM('Low', 'Medium', 'High') DEFAULT 'Low',
                responses JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """
        create_logs_table = """
            CREATE TABLE IF NOT EXISTS user_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                action VARCHAR(255),
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """
        try:
            cursor.execute(create_users_table)
            cursor.execute(create_results_table)
            cursor.execute(create_logs_table)
            conn.commit()
            print("✅ Database tables created successfully!")
        except pymysql.MySQLError as err:
            print(f"❌ Error creating tables: {err}")
        finally:
            cursor.close()
            conn.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def log_user_activity(user_id, action, details=None):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO user_logs (user_id, action, details, created_at) VALUES (%s, %s, %s, %s)",
                (user_id, action, details, datetime.now())
            )
            conn.commit()
        except pymysql.MySQLError as err:
            print(f"Error logging activity: {err}")
        finally:
            cursor.close()
            conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    if not email or not password:
        flash('Please fill in all fields.', 'error')
        return redirect(url_for('login'))
    if not validate_email(email):
        flash('Please enter a valid email address.', 'error')
        return redirect(url_for('login'))
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE email = %s AND is_active = TRUE", (email,))
            user = cursor.fetchone()
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                session['logged_in'] = True
                log_user_activity(user['id'], 'login')
                flash(f'Welcome back, {user["name"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password.', 'error')
        except pymysql.MySQLError as err:
            flash('Database error.', 'error')
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('login'))

@app.route('/register', methods=['POST'])
def register():
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    name = f"{first_name} {last_name}".strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')
    age = request.form.get('age')
    gender = request.form.get('gender', 'Other')
    occupation = request.form.get('occupation', '').strip()
    phone = ""
    address = occupation
    if not all([first_name, last_name, email, password, confirm_password]):
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('login'))
    if not validate_email(email):
        flash('Please enter a valid email address.', 'error')
        return redirect(url_for('login'))
    if password != confirm_password:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('login'))
    if len(password) < 6:
        flash('Password must be at least 6 characters.', 'error')
        return redirect(url_for('login'))
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('Email already exists.', 'error')
                return redirect(url_for('login'))
            hashed_pw = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO users (name, email, password, age, gender, phone, address)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, email, hashed_pw, int(age) if age else None, gender, phone, address))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except pymysql.MySQLError as err:
            flash('Registration error.', 'error')
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_name = session.get('user_name')
    recent_results = []
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, percentage, risk_level, message, created_at
                FROM results
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT 5
            """, (session['user_id'],))
            recent_results = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    return render_template('dashboard.html', user_name=user_name, recent_results=recent_results)

@app.route('/checklist', methods=['GET', 'POST'])
@login_required
def checklist():
    if request.method == 'POST':
        if not model or not scaler or not features:
            flash('Model files not loaded properly.', 'error')
            return redirect(url_for('checklist'))
        
        try:
            # Handle form data or JSON
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
            
            input_data = []
            for feature in features:
                if feature not in data:
                    flash(f'Missing feature: {feature}', 'error')
                    return redirect(url_for('checklist'))
                try:
                    input_data.append(float(data[feature]))
                except (ValueError, TypeError):
                    flash(f'Invalid value for {feature}: {data[feature]}', 'error')
                    return redirect(url_for('checklist'))

            # Scale input
            input_scaled = scaler.transform([input_data])

            # Predict
            prediction = model.predict(input_scaled)[0]
            percentage = round(prediction * 100, 2)  # Convert to percentage
            score = int(percentage)
            risk_level = 'Low'
            if percentage > 66.67:
                risk_level = 'High'
            elif percentage > 33.33:
                risk_level = 'Medium'
            message = f"ADHD Confidence Score: {round(prediction, 2)}. Higher scores may suggest attention challenges. Consult a professional for advice."

            # Save to database
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        INSERT INTO results (user_id, score, percentage, message, risk_level, responses)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (session['user_id'], score, percentage, message, risk_level, str(data)))
                    conn.commit()
                    result_id = cursor.lastrowid
                    log_user_activity(session['user_id'], 'prediction', f"Predicted ADHD Confidence Score: {percentage}")
                except pymysql.MySQLError as err:
                    flash(f"Error saving result: {err}", 'error')
                    return redirect(url_for('checklist'))
                finally:
                    cursor.close()
                    conn.close()

            # Redirect to result page
            return redirect(url_for('result', result_id=result_id))
        except Exception as e:
            flash(f"Prediction error: {str(e)}", 'error')
            return redirect(url_for('checklist'))

    return render_template('checklist.html', features=features)

@app.route('/profile')
@login_required
def profile():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('profile.html', user=user)

@app.route('/result/<int:result_id>')
@login_required
def result(result_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM results WHERE id = %s AND user_id = %s", (result_id, session['user_id']))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('result.html', result=result)

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        log_user_activity(session['user_id'], 'logout')
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

@app.context_processor
def inject_user():
    return dict(
        logged_in=session.get('logged_in', False),
        user_name=session.get('user_name', ''),
        user_email=session.get('user_email', '')
    )

if __name__ == '__main__':
    print("🚀 Starting ADHD Screening Platform...")
    print("📊 Initializing database...")
    init_db()
    print("✅ Database initialized!")
    print("🌐 Access the app at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)