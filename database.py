import sqlite3
from datetime import datetime

# 🔹 Database connection
conn = sqlite3.connect("usdt.db", check_same_thread=False)
cur = conn.cursor()

# =========================
# TABLES (AUTO CREATE)
# =========================

# 👤 Users table
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    uid TEXT PRIMARY KEY,
    chat_id INTEGER,
    upi TEXT
)
""")

# 📦 Orders table
cur.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid TEXT,
    amount REAL,
    status TEXT,
    created_at TEXT
)
""")

conn.commit()

# =========================
# USER FUNCTIONS
# =========================

def save_user(uid, chat_id):
    cur.execute(
        "INSERT OR IGNORE INTO users (uid, chat_id) VALUES (?, ?)",
        (uid, chat_id)
    )
    conn.commit()


def update_upi(uid, upi):
    cur.execute(
        "UPDATE users SET upi=? WHERE uid=?",
        (upi, uid)
    )
    conn.commit()


def get_user_by_uid(uid):
    cur.execute(
        "SELECT uid, chat_id, upi FROM users WHERE uid=?",
        (uid,)
    )
    return cur.fetchone()

# =========================
# ORDER FUNCTIONS
# =========================

def create_order(uid):
    cur.execute(
        "INSERT INTO orders (uid, status, created_at) VALUES (?, ?, ?)",
        (uid, "PENDING", datetime.now().isoformat())
    )
    conn.commit()
    return cur.lastrowid


def update_order_amount(order_id, amount):
    cur.execute(
        "UPDATE orders SET amount=? WHERE id=?",
        (amount, order_id)
    )
    conn.commit()


def update_order_status(order_id, status):
    cur.execute(
        "UPDATE orders SET status=? WHERE id=?",
        (status, order_id)
    )
    conn.commit()


def get_orders(uid):
    cur.execute(
        "SELECT id, amount, status, created_at FROM orders WHERE uid=? ORDER BY id DESC",
        (uid,)
    )
    return cur.fetchall()


def get_order_by_id(order_id):
    cur.execute(
        "SELECT id, uid, amount, status, created_at FROM orders WHERE id=?",
        (order_id,)
    )
    return cur.fetchone()

def get_orders(uid):
    cur.execute(
        "SELECT id, amount, status, created_at FROM orders WHERE uid=?",
        (uid,)
    )
    return cur.fetchall()

def admin_update_order(order_id, status, amount=None):
    if amount is not None:
        cur.execute(
            "UPDATE orders SET status=?, amount=? WHERE id=?",
            (status, amount, order_id)
        )
    else:
        cur.execute(
            "UPDATE orders SET status=? WHERE id=?",
            (status, order_id)
        )
    conn.commit()

def get_chat_id(uid):
    cur.execute("SELECT chat_id FROM users WHERE uid=?", (uid,))
    row = cur.fetchone()
    return row[0] if row else None

