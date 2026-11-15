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

    print("Seeding initial database records...")

    # Seed Teacher User
    teacher_pw = generate_password_hash("admin123")
    cursor.execute('''
    INSERT INTO users (username, password_hash, full_name, email, role)
    VALUES (?, ?, ?, ?, ?)
    ''', ('ogretmen', teacher_pw, 'Prof. Dr. Ahmet Yılmaz', 'ahmet.yilmaz@universite.edu.tr', 'teacher'))
    teacher_id = cursor.lastrowid

    # Seed Courses
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

    # Seed Realistic Turkish Students Roster
    students_data = [
        ('202301001', 'Zeynep Kaya', 'zeynep.kaya@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301002', 'Mehmet Can Demir', 'mehmet.demir@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301003', 'Ayşe Nur Çelik', 'ayse.celik@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301004', 'Emre Şahin', 'emre.sahin@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301005', 'Elif Yıldırım', 'elif.yildirim@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301006', 'Burak Öztürk', 'burak.ozturk@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301007', 'Selin Aydın', 'selin.aydin@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301008', 'Ali Kemal Aksoy', 'ali.aksoy@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301009', 'Büşra Doğan', 'busra.dogan@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301010', 'Deniz Arslan', 'deniz.arslan@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301011', 'Onur Koç', 'onur.koc@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301012', 'Fatma Keskin', 'fatma.keskin@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301013', 'Hakan Kurt', 'hakan.kurt@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301014', 'Gamze Polat', 'gamze.polat@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301015', 'Kaan Çetin', 'kaan.cetin@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301016', 'Merve Aslan', 'merve.aslan@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301017', 'Serkan Yavuz', 'serkan.yavuz@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301018', 'İrem Şimşek', 'irem.simsek@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301019', 'Tolga Taş', 'tolga.tas@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301020', 'Gizem Eren', 'gizem.eren@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301021', 'Mustafa Gül', 'mustafa.gul@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301022', 'Ceren Bozkurt', 'ceren.bozkurt@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301023', 'Oğuzhan Tekin', 'oguzhan.tekin@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301024', 'Kübra Özdemir', 'kubra.ozdemir@ogr.edu.tr', 'Yazılım Mühendisliği', 3),
        ('202301025', 'Barış Güler', 'baris.guler@ogr.edu.tr', 'Yazılım Mühendisliği', 3)
    ]

    student_ids = []
    for s in students_data:
        cursor.execute('''
        INSERT INTO students (student_number, full_name, email, department, class_year)
        VALUES (?, ?, ?, ?, ?)
        ''', s)
        student_ids.append(cursor.lastrowid)

    # Enroll all students in Course 1 (YAZ401) and Course 2 (CEN205)
    for cid in [course_ids[0], course_ids[1]]:
        for sid in student_ids:
            cursor.execute('''
            INSERT INTO course_enrollments (course_id, student_id)
            VALUES (?, ?)
            ''', (cid, sid))

    # Enroll first 15 students in Course 3 (BİL102)
    for sid in student_ids[:15]:
        cursor.execute('''
        INSERT INTO course_enrollments (course_id, student_id)
        VALUES (?, ?)
        ''', (course_ids[2], sid))

    # Seed 2 Past Attendance Sessions for Course 1 so reports have historical data
    # Past Session 1 (Week 1)
    d1 = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d 10:00:00')
    cursor.execute('''
    INSERT INTO attendance_sessions (course_id, title, week_number, secret_key, status, started_at, closed_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (course_ids[0], 'Hafta 1 - Mimari Desenlere Giriş', 1, 'sec_w1_sample', 'CLOSED', d1, d1))
    s1_id = cursor.lastrowid

    # 22 students were present, 1 late, 2 absent
    for idx, sid in enumerate(student_ids):
        if idx < 22:
            st = 'PRESENT'
        elif idx == 22:
            st = 'LATE'
        else:
            st = 'ABSENT'
        cursor.execute('''
        INSERT INTO attendance_records (session_id, student_id, status, method, scanned_at, ip_address)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (s1_id, sid, st, 'QR', d1, '192.168.1.' + str(100 + idx)))

    # Past Session 2 (Week 2)
    d2 = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d 10:00:00')
    cursor.execute('''
    INSERT INTO attendance_sessions (course_id, title, week_number, secret_key, status, started_at, closed_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (course_ids[0], 'Hafta 2 - Mikroservis Mimarisi', 2, 'sec_w2_sample', 'CLOSED', d2, d2))
    s2_id = cursor.lastrowid

    for idx, sid in enumerate(student_ids):
        if idx < 20:
            st = 'PRESENT'
        elif idx in [20, 21]:
            st = 'EXCUSED'
        else:
            st = 'ABSENT'
        cursor.execute('''
        INSERT INTO attendance_records (session_id, student_id, status, method, scanned_at, ip_address)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (s2_id, sid, st, 'QR' if st != 'EXCUSED' else 'MANUAL', d2, '192.168.1.' + str(100 + idx)))

    conn.commit()
    print("Database successfully seeded with realistic sample data!")

if __name__ == '__main__':
    init_db()
