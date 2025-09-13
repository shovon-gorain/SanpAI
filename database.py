import sqlite3
from werkzeug.security import generate_password_hash

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            is_paid INTEGER DEFAULT 0,
            profile_image TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Videos table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            video_url TEXT NOT NULL,
            title TEXT,
            music_style TEXT NOT NULL,
            music_file TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Login attempts table (for security)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            attempts INTEGER DEFAULT 0,
            last_attempt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create default admin user if not exists
    admin_email = 'admin@reelcraft.ai'
    admin_password = generate_password_hash('admin123')
    
    if not conn.execute('SELECT * FROM users WHERE email = ?', (admin_email,)).fetchone():
        conn.execute(
            'INSERT INTO users (name, email, password, is_admin, is_paid) VALUES (?, ?, ?, ?, ?)',
            ('Admin User', admin_email, admin_password, 1, 1)
        )
    
    conn.commit()
    conn.close()

def add_user(name, email, password, is_admin, is_paid):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO users (name, email, password, is_admin, is_paid) VALUES (?, ?, ?, ?, ?)',
        (name, email, password, is_admin, is_paid)
    )
    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE email = ?', (email,)
    ).fetchone()
    conn.close()
    return user

def get_all_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return users

def get_all_videos():
    conn = get_db_connection()
    videos = conn.execute('''
        SELECT videos.*, users.name as user_name 
        FROM videos 
        JOIN users ON videos.user_id = users.id
    ''').fetchall()
    conn.close()
    return videos

def get_videos_by_user(user_id):
    conn = get_db_connection()
    videos = conn.execute(
        'SELECT * FROM videos WHERE user_id = ? ORDER BY created_at DESC', 
        (user_id,)
    ).fetchall()
    conn.close()
    return videos

def add_video(user_id, video_url, music_style, title=None, music_file=None):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO videos (user_id, video_url, music_style, title, music_file) VALUES (?, ?, ?, ?, ?)',
        (user_id, video_url, music_style, title, music_file)
    )
    conn.commit()
    conn.close()

def increment_login_attempts(email):
    conn = get_db_connection()
    attempt = conn.execute(
        'SELECT * FROM login_attempts WHERE email = ?', (email,)
    ).fetchone()
    
    if attempt:
        conn.execute(
            'UPDATE login_attempts SET attempts = attempts + 1, last_attempt = CURRENT_TIMESTAMP WHERE email = ?',
            (email,)
        )
    else:
        conn.execute(
            'INSERT INTO login_attempts (email, attempts) VALUES (?, 1)',
            (email,)
        )
    
    conn.commit()
    conn.close()

def reset_login_attempts(email):
    conn = get_db_connection()
    conn.execute(
        'DELETE FROM login_attempts WHERE email = ?',
        (email,)
    )
    conn.commit()
    conn.close()

def get_login_attempts(email):
    conn = get_db_connection()
    attempt = conn.execute(
        'SELECT attempts FROM login_attempts WHERE email = ?', (email,)
    ).fetchone()
    conn.close()
    
    return attempt[0] if attempt else 0

def update_payment_status(user_id, is_paid):
    conn = get_db_connection()
    conn.execute(
        'UPDATE users SET is_paid = ? WHERE id = ?',
        (is_paid, user_id)
    )
    conn.commit()
    conn.close()