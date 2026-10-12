import sqlite3
from datetime import datetime, timedelta

ADMIN_IDS = [8475640967]

def get_db_connection():
    conn = sqlite3.connect('database.db', timeout=20)
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            expiry_date TEXT DEFAULT '2000-01-01 00:00:00'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY
        )
    ''')
    for aid in ADMIN_IDS:
        cursor.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (aid,))
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'expiry_date' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN expiry_date TEXT DEFAULT '2000-01-01 00:00:00'")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_files (
            filename TEXT PRIMARY KEY
        )
    ''')
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS search_index USING fts5(
            filename,
            content
        )
    ''')
    conn.commit()
    conn.close()

def is_admin(user_id):
    if user_id in ADMIN_IDS:
        return True
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM admins WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def get_all_admin_ids():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM admins')
    db_admins = [row[0] for row in cursor.fetchall()]
    conn.close()
    return list(set(ADMIN_IDS + db_admins))

def add_admin_db(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def remove_admin_db(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM admins WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_user_expiry(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT expiry_date FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        try:
            return datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
    return datetime(2000, 1, 1)

def add_user_subscription(user_id, days):
    current_exp = get_user_expiry(user_id)
    now = datetime.now()
    start_base = current_exp if current_exp > now else now
    new_exp = start_base + timedelta(days=days)
    exp_str = new_exp.strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, expiry_date) VALUES (?, ?)', (user_id, exp_str))
    cursor.execute('UPDATE users SET expiry_date = ? WHERE user_id = ?', (exp_str, user_id))
    conn.commit()
    conn.close()
    return new_exp

def has_access(user_id):
    if is_admin(user_id):
        return True
    exp = get_user_expiry(user_id)
    return exp > datetime.now()

def get_validity_str(user_id):
    if is_admin(user_id):
        return "Unlimited (Admin)"
    exp = get_user_expiry(user_id)
    now = datetime.now()
    if exp > now:
        remaining = exp - now
        days = remaining.days
        hours = remaining.seconds // 3600
        return f"Active ({days}d {hours}h left)"
    else:
        return "Plan Expired"
  
