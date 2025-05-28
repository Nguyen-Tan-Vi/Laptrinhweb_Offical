from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_PATH = 'db.sqlite3'

def init_db():
    if not os.path.exists(DB_PATH):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                email TEXT,
                fullname TEXT,
                phone TEXT,
                avatar_url TEXT,
                bio TEXT
            )''')

init_db()

def get_user_by_credentials(username, password):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        return cur.fetchone()

def get_user_by_id(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
        return cur.fetchone()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = (
            request.form['username'],
            request.form['password'],
            request.form['email'],
            request.form['fullname'],
            request.form['phone'],
            request.form['avatar_url'],
            request.form['bio']
        )
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute('''
                    INSERT INTO users (username, password, email, fullname, phone, avatar_url, bio)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', data)
            return redirect(url_for('login'))
        except:
            return "Tài khoản đã tồn tại!"

    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = get_user_by_credentials(request.form['username'], request.form['password'])
        if user:
            session['user_id'] = user[0]
            return redirect(url_for('profile'))
        return "Sai tên đăng nhập hoặc mật khẩu!"
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = get_user_by_id(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = (
            request.form['fullname'],
            request.form['email'],
            request.form['phone'],
            request.form['avatar_url'],
            request.form['bio'],
            session['user_id']
        )
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('''
                UPDATE users SET fullname=?, email=?, phone=?, avatar_url=?, bio=?
                WHERE id=?
            ''', data)
        return redirect(url_for('profile'))

    user = get_user_by_id(session['user_id'])
    return render_template('edit_profile.html', user=user)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

AVATAR_FOLDER = r'C:/Users/ADMIN/OneDrive/Pictures/Saved Pictures'

@app.route('/avatar/<filename>')
def avatar_file(filename):
    return send_from_directory(AVATAR_FOLDER, filename)

