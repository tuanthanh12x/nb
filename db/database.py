import sqlite3
import hashlib
import sys
import os
from pathlib import Path

# Determine correct base directory
if getattr(sys, 'frozen', False):
    # If the app is bundled by PyInstaller
    BASE_DIR = Path(os.path.dirname(sys.executable))
else:
    # If running in development
    BASE_DIR = Path(__file__).resolve().parent.parent

# Path to the SQLite database file
DB_PATH = BASE_DIR / "data" / "app.db"


def get_conn():
    """Establish and return a database connection."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Initialize the database, create folders and tables if needed."""
    # Ensure data folder exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = get_conn()
    cursor = conn.cursor()

    # Create user table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


def get_all_users():
    """Return a list of (id, username) for all users."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    results = cursor.fetchall()
    conn.close()
    return results


def verify_login(username, password):
    """Check if the username and hashed password match a user in the DB."""
    hashed = hashlib.sha256(password.encode()).hexdigest()
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password_hash=?", (username, hashed))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def create_user(username, password):
    """Create a new user if username does not exist."""
    hashed = hashlib.sha256(password.encode()).hexdigest()
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed))
        conn.commit()
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()
    return True
