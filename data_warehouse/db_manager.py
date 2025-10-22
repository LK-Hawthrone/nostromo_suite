import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "nostromo_auth.db"

class DBManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._create_tables()

    def _connect(self):
        """Return a SQLite connection object."""
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        """Create students and teachers tables if they don't exist."""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    ra TEXT UNIQUE NOT NULL,
                    course TEXT NOT NULL,
                    period INTEGER NOT NULL,
                    agreed_eula BOOLEAN NOT NULL CHECK (agreed_eula IN (0,1)),
                    passed_captcha BOOLEAN NOT NULL CHECK (passed_captcha IN (0,1)),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    registration_number TEXT UNIQUE NOT NULL,
                    agreed_eula BOOLEAN NOT NULL CHECK (agreed_eula IN (0,1)),
                    passed_captcha BOOLEAN NOT NULL CHECK (passed_captcha IN (0,1)),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    # STUDENTS
    def insert_student(self, student_data: dict):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO students
                    (name, email, password, ra, course, period, agreed_eula, passed_captcha)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    student_data['name'],
                    student_data['email'],
                    student_data['password'],
                    student_data['ra'],
                    student_data['course'],
                    student_data['period'],
                    int(student_data['agreed_eula']),
                    int(student_data['passed_captcha'])
                ))
                conn.commit()
                return True
        except sqlite3.IntegrityError as e:
            print(f"[ERROR] Failed to insert student: {e}")
            return False

    def get_student_by_email(self, email: str):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE email = ?", (email,))
            return cursor.fetchone()

    # TEACHERS
    def insert_teacher(self, teacher_data: dict):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO teachers
                    (name, email, password, registration_number, agreed_eula, passed_captcha)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    teacher_data['name'],
                    teacher_data['email'],
                    teacher_data['password'],
                    teacher_data['registration_number'],
                    int(teacher_data['agreed_eula']),
                    int(teacher_data['passed_captcha'])
                ))
                conn.commit()
                return True
        except sqlite3.IntegrityError as e:
            print(f"[ERROR] Failed to insert teacher: {e}")
            return False

    def get_teacher_by_email(self, email: str):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM teachers WHERE email = ?", (email,))
            return cursor.fetchone()
