import sqlite3
from core.hash_manager import secure_store, verify_hash

DB_PATH = "data_warehouse/nostromo.db"

# -----------------------------
# Basic database setup
# -----------------------------

def connect_db():
    """Connect to the SQLite database and return the connection and cursor."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    return conn, cursor


def create_tables():
    """Create basic tables for students and teachers if they don't exist."""
    conn, cursor = connect_db()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            salt TEXT NOT NULL,
            ra TEXT NOT NULL,
            course TEXT NOT NULL,
            period INTEGER NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            salt TEXT NOT NULL,
            registration TEXT NOT NULL
        );
    """)

    conn.commit()
    conn.close()
    print("[DB] Tables are ready.")


# -----------------------------
# Insert operations
# -----------------------------

def insert_student(name, email, password, ra, course, period):
    """Insert a new student with hashed password."""
    conn, cursor = connect_db()
    hashed_password, salt = secure_store(password)

    try:
        cursor.execute("""
            INSERT INTO students (name, email, hashed_password, salt, ra, course, period)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (name, email, hashed_password, salt, ra, course, period))
        conn.commit()
        print(f"[DB] Student '{name}' registered successfully!")
        success = True
    except Exception as e:
        conn.rollback()
        print(f"[DB ERROR] Could not register student: {e}")
        success = False
    finally:
        conn.close()
    return success


def insert_teacher(name, email, password, registration):
    """Insert a new teacher with hashed password."""
    conn, cursor = connect_db()
    hashed_password, salt = secure_store(password)

    try:
        cursor.execute("""
            INSERT INTO teachers (name, email, hashed_password, salt, registration)
            VALUES (?, ?, ?, ?, ?);
        """, (name, email, hashed_password, salt, registration))
        conn.commit()
        print(f"[DB] Teacher '{name}' registered successfully!")
        success = True
    except Exception as e:
        conn.rollback()
        print(f"[DB ERROR] Could not register teacher: {e}")
        success = False
    finally:
        conn.close()
    return success


# -----------------------------
# Login / verification
# -----------------------------

def verify_user(email, password, user_type="student"):
    """Check if a student or teacher exists and verify password."""
    conn, cursor = connect_db()

    table = "students" if user_type == "student" else "teachers"
    cursor.execute(f"SELECT hashed_password, salt FROM {table} WHERE email = ?", (email,))
    record = cursor.fetchone()
    conn.close()

    if not record:
        print(f"[AUTH] {user_type.title()} not found.")
        return False

    stored_hash, salt = record
    if verify_hash(password, salt, stored_hash):
        print(f"[AUTH] {user_type.title()} successfully authenticated!")
        return True
    else:
        print(f"[AUTH] Invalid credentials for {user_type}.")
        return False


# -----------------------------
# Initialize database when module runs
# -----------------------------

if __name__ == "__main__":
    create_tables()
