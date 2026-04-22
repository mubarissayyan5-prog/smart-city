from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import re
import numpy as np

app = Flask(__name__)
app.secret_key = '1122'

# ---------------------------
# Database Connection
# ---------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="", 
        database="smartcity_db"
    )
    


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/methodology')
def methodology():
    return render_template('methodology.html')

# ---------------------------
# SIGN UP
# ---------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form['uname']
        email = request.form['email']
        password = request.form['password']

        # Basic validation
        if not uname.strip():
            flash("Username is required", "danger")
            return redirect(url_for('register'))

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email address", "danger")
            return redirect(url_for('register'))

        if len(password) < 6:
            flash("Password must be at least 6 characters", "danger")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check existing email
        cursor.execute("SELECT u_id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash("Email already registered", "danger")
            cursor.close()
            conn.close()
            return redirect(url_for('register'))

        # Insert user
        cursor.execute(
            "INSERT INTO users (uname, email, password) VALUES (%s, %s, %s)",
            (uname, email, hashed_password)
        )
        conn.commit()

        cursor.close()
        conn.close()

        flash("Registration successful. Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# ---------------------------
# LOGIN
# ---------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email address", "danger")
            return redirect(url_for('login'))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['u_id']
            session['username'] = user['uname']
            return redirect(url_for('index'))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

# ---------------------------
# LOGOUT
# ---------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



# ---------------------------
# RUN APP
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)