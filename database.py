
import sqlite3
import hashlib
import secrets
import hmac

DB_NAME = "nova_ai.db"


# Database connection
def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# Create database tables
def create_tables():
    with connect_db() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id)
                REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(chat_id)
                REFERENCES chats(id) ON DELETE CASCADE
            )
        """)


# Password hashing
def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200000
    ).hex()


# Register user
def register_user(username, password):
    username = username.strip()

    salt = secrets.token_hex(16)
    password_hash = hash_password(password, salt)

    try:
        with connect_db() as conn:
            conn.execute(
                """
                INSERT INTO users
                (username, password_hash, salt)
                VALUES (?, ?, ?)
                """,
                (username, password_hash, salt)
            )

        return True

    except sqlite3.IntegrityError:
        return False


# Login user
def login_user(username, password):
    with connect_db() as conn:
        user = conn.execute(
            """
            SELECT id, password_hash, salt
            FROM users
            WHERE username = ?
            """,
            (username.strip(),)
        ).fetchone()

    if user:
        user_id, saved_hash, salt = user
        entered_hash = hash_password(password, salt)

        if hmac.compare_digest(saved_hash, entered_hash):
            return user_id

    return None


# Create new chat
def create_chat(user_id, title="New Chat"):
    with connect_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO chats (user_id, title)
            VALUES (?, ?)
            """,
            (user_id, title)
        )

        return cursor.lastrowid


# Get user's chats
def get_user_chats(user_id):
    with connect_db() as conn:
        chats = conn.execute(
            """
            SELECT id, title
            FROM chats
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (user_id,)
        ).fetchall()

    return chats


# Get messages
def get_messages(chat_id, user_id):
    with connect_db() as conn:
        messages = conn.execute(
            """
            SELECT role, content
            FROM messages
            WHERE chat_id = ?
            AND chat_id IN (
                SELECT id FROM chats
                WHERE user_id = ?
            )
            ORDER BY id
            """,
            (chat_id, user_id)
        ).fetchall()

    return [
        {"role": role, "content": content}
        for role, content in messages
    ]


# Save message
def save_message(chat_id, role, content, user_id):
    with connect_db() as conn:
        conn.execute(
            """
            INSERT INTO messages (chat_id, role, content)
            SELECT ?, ?, ?
            WHERE EXISTS (
                SELECT 1 FROM chats
                WHERE id = ? AND user_id = ?
            )
            """,
            (chat_id, role, content, chat_id, user_id)
        )


# Update chat title
def update_chat_title(chat_id, user_id, title):
    with connect_db() as conn:
        conn.execute(
            """
            UPDATE chats
            SET title = ?
            WHERE id = ? AND user_id = ?
            """,
            (title, chat_id, user_id)
        )


# Delete chat
def delete_chat(chat_id, user_id):
    with connect_db() as conn:
        conn.execute(
            """
            DELETE FROM chats
            WHERE id = ? AND user_id = ?
            """,
            (chat_id, user_id)
        )
