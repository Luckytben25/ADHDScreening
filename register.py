from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
import pymysql
from pymysql.cursors import DictCursor
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Default XAMPP password is blank
    'database': 'adhd',
    'cursorclass': DictCursor
}

# Utility: Email validation
def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Connect to MySQL
def get_db_connection():
    try:
        return pymysql.connect(**DB_CONFIG)
    except Exception as e:
        print(f"MySQL Connection Error: {e}")
        return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form inputs
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email').lower()
        age = request.form.get('age')
        gender = request.form.get('gender')
        occupation = request.form.get('occupation')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validation
        if not all([first_name, last_name, email, age, gender, occupation, password, confirm_password]):
            flash("Please fill in all required fields.", "error")
            return render_template("login.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("login.html")

        if not validate_email(email):
            flash("Invalid email format.", "error")
            return render_template("login.html")

        # Save user to database
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            try:
                # Check if email already exists
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash("Email is already registered.", "error")
                    return render_template("login.html")

                # Insert new user
                hashed_password = generate_password_hash(password)
                cursor.execute("""
                               INSERT INTO users (first_name, last_name, email, age, gender, occupation, password)
                               VALUES (%s, %s, %s, %s, %s, %s, %s)
                               """, (first_name, last_name, email, age, gender, occupation, hashed_password))
                connection.commit()

                flash("Registration successful! Please log in.", "success")
                return redirect(url_for('login'))
            except Exception as e:
                flash(f"Error: {e}", "error")
            finally:
                cursor.close()
                connection.close()
        else:
            flash("Database connection failed.", "error")

    return render_template("login.html")
