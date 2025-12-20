from flask import Flask, render_template, request, redirect, url_for, session, flash
import gspread
from google.oauth2.service_account import Credentials
import bcrypt
import re
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(minutes=30)

# Database
def connect_to_database():
    credentials = Credentials.from_service_account_file(
        'credentials.json',
        scopes=[
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
    )
    client = gspread.authorize(credentials)
    return client.open('UserDatabase').sheet1


# Validation
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def check_password_strength(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least 1 uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least 1 lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least 1 number"
    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
        return False, "Password must contain at least 1 special character"
    return True, "Strong password"


# Database Helpers
def username_exists(username):
    sheet = connect_to_database()
    return username in sheet.col_values(1)[1:]


def email_exists(email):
    sheet = connect_to_database()
    return email in sheet.col_values(2)[1:]


def get_user_by_email(email):
    sheet = connect_to_database()
    users = sheet.get_all_values()[1:]

    for row_num, row in enumerate(users, start=2):
        if len(row) >= 2 and row[1] == email:
            while len(row) < 5:
                row.append('')
            return {
                'row_number': row_num,
                'username': row[0],
                'email': row[1],
                'password': row[2],
                'failed_attempts': int(row[3]) if row[3] else 0,
                'lock_until': row[4]
            }
    return None


def create_new_user(username, email, password):
    sheet = connect_to_database()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    sheet.append_row([username, email, hashed, 0, ''])


def update_failed_attempts(user, count):
    sheet = connect_to_database()

    if count >= 4:
        lock_until = (datetime.now() + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
        sheet.update_cell(user['row_number'], 4, count)
        sheet.update_cell(user['row_number'], 5, lock_until)
        return True
    else:
        sheet.update_cell(user['row_number'], 4, count)
        return False


def reset_failed_attempts(user):
    sheet = connect_to_database()
    sheet.update_cell(user['row_number'], 4, 0)
    sheet.update_cell(user['row_number'], 5, '')


def is_account_locked(user):
    if not user['lock_until']:
        return False, None

    lock_time = datetime.strptime(user['lock_until'], '%Y-%m-%d %H:%M:%S')
    if datetime.now() < lock_time:
        minutes = int((lock_time - datetime.now()).total_seconds() / 60)
        return True, f"Account locked. Try again in {minutes} minutes."

    reset_failed_attempts(user)
    return False, None


# Routes
@app.route('/')
def home():
    return redirect(url_for('dashboard')) if 'username' in session else redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template('signup.html', username=username, email=email)

        if username_exists(username):
            flash('Username already taken', 'error')
            return render_template('signup.html', username=username, email=email)

        if not is_valid_email(email):
            flash('Invalid email format', 'error')
            return render_template('signup.html', username=username, email=email)

        if email_exists(email):
            flash('Email already registered', 'error')
            return render_template('signup.html', username=username, email=email)

        strong, msg = check_password_strength(password)
        if not strong:
            flash(msg, 'error')
            return render_template('signup.html', username=username, email=email)

        create_new_user(username, email, password)
        flash('Account created successfully. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        user = get_user_by_email(email)
        if not user:
            flash('Email not found', 'error')
            return render_template('login.html', email=email)

        locked, msg = is_account_locked(user)
        if locked:
            flash(msg, 'error')
            return render_template('login.html', email=email)

        if bcrypt.checkpw(password.encode(), user['password'].encode()):
            reset_failed_attempts(user)
            session.permanent = True
            session['username'] = user['username']
            session['email'] = user['email']
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))

        attempts = user['failed_attempts'] + 1
        locked = update_failed_attempts(user, attempts)
        flash(
            'Too many attempts. Account locked.' if locked
            else f'Incorrect password. {4 - attempts} attempts remaining.',
            'error'
        )
        return render_template('login.html', email=email)

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
