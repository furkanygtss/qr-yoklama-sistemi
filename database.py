"""
Database module for QR Attendance System.
Handles SQLite connection, schema creation, and realistic sample data seeding.
"""
import sqlite3
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'attendance.db')

def get_db():
    try:
        from flask import g
        if 'db' not in g:
            g.db = sqlite3.connect(DB_PATH)
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db
    except (ImportError, RuntimeError):
        # Fallback when run outside of Flask app context (e.g. scripts, seeds)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

def init_db(seed=True):
    conn = get_db()
    cursor = conn.cursor()

    # 1. Users table (Teachers / Admins)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE,
        role TEXT NOT NULL DEFAULT 'teacher', -- 'teacher', 'admin'
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2. Courses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        name TEXT NOT NULL,
        semester TEXT NOT NULL,
        academic_year TEXT NOT NULL,
        teacher_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE SET NULL
    )
    ''')

    # 3. Students table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_number TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE,
        department TEXT NOT NULL,
        class_year INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 4. Course Enrollment (Many-to-Many between Courses and Students)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS course_enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(course_id, student_id),
        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    ''')

    # 5. Attendance Sessions
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        week_number INTEGER DEFAULT 1,
        secret_key TEXT NOT NULL,
        token_interval_seconds INTEGER DEFAULT 15,
        status TEXT NOT NULL DEFAULT 'ACTIVE', -- 'ACTIVE', 'CLOSED'
        started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        closed_at DATETIME,
        require_location INTEGER DEFAULT 0,
        latitude REAL,
        longitude REAL,
        radius_meters INTEGER DEFAULT 100,
        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
    )
    ''')

    # 6. Attendance Records
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'PRESENT', -- 'PRESENT', 'LATE', 'EXCUSED', 'ABSENT'
        method TEXT NOT NULL DEFAULT 'QR', -- 'QR', 'MANUAL'
        scanned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        ip_address TEXT,
        user_agent TEXT,
        UNIQUE(session_id, student_id),
        FOREIGN KEY (session_id) REFERENCES attendance_sessions(id) ON DELETE CASCADE,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    ''')

    conn.commit()

    if seed:
        seed_data(conn)

    conn.close()

def seed_data(conn):
    cursor = conn.cursor()

    # Check if users already exist
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        return # Data already seeded

    print("Seeding database with real instructor and students...")

    # Seed Teacher: Ahmet Deniz (supports username: 'ahmetdeniz' and 'ogretmen')
    teacher_pw = generate_password_hash("admin123")
    cursor.execute('''
    INSERT INTO users (username, password_hash, full_name, email, role)
    VALUES (?, ?, ?, ?, ?)
    ''', ('ahmetdeniz', teacher_pw, 'Ahmet Deniz', 'ahmet.deniz@universite.edu.tr', 'teacher'))
    teacher_id = cursor.lastrowid

    # Also keep 'ogretmen' alias for quick fallback
    cursor.execute('''
    INSERT INTO users (username, password_hash, full_name, email, role)
    VALUES (?, ?, ?, ?, ?)
    ''', ('ogretmen', teacher_pw, 'Ahmet Deniz', 'ogretmen@universite.edu.tr', 'teacher'))

    # Seed Courses for Ahmet Deniz
    courses_data = [
        ('YAZ401', 'Yazılım Mimarisi ve Tasarımı', 'Güz', '2026-2027', teacher_id),
        ('CEN205', 'Veri Tabanı Yönetim Sistemleri', 'Güz', '2026-2027', teacher_id),
        ('BİL102', 'Nesne Yönelimli Programlama', 'Güz', '2026-2027', teacher_id)
    ]
    course_ids = []
    for c in courses_data:
        cursor.execute('''
        INSERT INTO courses (code, name, semester, academic_year, teacher_id)
        VALUES (?, ?, ?, ?, ?)
        ''', c)
        course_ids.append(cursor.lastrowid)

    # Real Students List
    students_data = [
        ('252302034', 'Furkan Yiğit Koygun', 'furkan.koygun@ogr.edu.tr', 'Bilgisayar ve Yazılım Mühendisliği', 2),
        ('252302035', 'Ahmet Yılmaz', 'ahmet.yilmaz@ogr.edu.tr', 'Bilgisayar ve Yazılım Mühendisliği', 2),
        ('252302036', 'Mehmet Kaya', 'mehmet.kaya@ogr.edu.tr', 'Bilgisayar ve Yazılım Mühendisliği', 2),
        ('252302037', 'Zeynep Demir', 'zeynep.demir@ogr.edu.tr', 'Bilgisayar ve Yazılım Mühendisliği', 2),
        ('252302038', 'Ali Çelik', 'ali.celik@ogr.edu.tr', 'Bilgisayar ve Yazılım Mühendisliği', 2)
    ]

    student_ids = []
    for s in students_data:
        cursor.execute('''
        INSERT INTO students (student_number, full_name, email, department, class_year)
        VALUES (?, ?, ?, ?, ?)
        ''', s)
        student_ids.append(cursor.lastrowid)

    # Enroll all 5 students in all courses
    for cid in course_ids:
        for sid in student_ids:
            cursor.execute('''
            INSERT INTO course_enrollments (course_id, student_id)
            VALUES (?, ?)
            ''', (cid, sid))

    # Past Session 1 (Week 1) for reporting demo
    d1 = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d 10:00:00')
    cursor.execute('''
    INSERT INTO attendance_sessions (course_id, title, week_number, secret_key, status, started_at, closed_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (course_ids[0], 'Hafta 1 - Giriş ve Temel Kavramlar', 1, 'sec_w1_sample', 'CLOSED', d1, d1))
    s1_id = cursor.lastrowid

    # 4 students present, 1 late in past session
    for idx, sid in enumerate(student_ids):
        st = 'PRESENT' if idx < 4 else 'LATE'
        cursor.execute('''
        INSERT INTO attendance_records (session_id, student_id, status, method, scanned_at, ip_address)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (s1_id, sid, st, 'QR', d1, '192.168.1.' + str(100 + idx)))

    conn.commit()
    print("Database successfully seeded with real Ahmet Deniz and 5 students!")

if __name__ == '__main__':
    init_db()
