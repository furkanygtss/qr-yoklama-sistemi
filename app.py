"""
Main Flask Application for QR Attendance System.
Provides teacher dashboard, live dynamic QR projection, mobile student check-in, and attendance reports.
"""
import os
import uuid
import csv
import io
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, flash, Response, make_response, g
)
from werkzeug.security import check_password_hash

from database import get_db, init_db
from token_service import get_current_token_info, verify_token, get_server_ip

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "qr_attendance_super_secret_key_2026")

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# ----------------- Decorators & Helpers -----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Lütfen önce giriş yapınız.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_global_data():
    server_ip = get_server_ip()
    user_info = None
    if 'user_id' in session:
        user_info = {
            'id': session.get('user_id'),
            'username': session.get('username'),
            'full_name': session.get('full_name'),
            'role': session.get('role')
        }
    return dict(server_ip=server_ip, current_user=user_info)


# ----------------- Authentication Routes -----------------
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('teacher_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            flash(f"Hoş geldiniz, {user['full_name']}!", "success")
            return redirect(url_for('teacher_dashboard'))
        else:
            flash("Geçersiz kullanıcı adı veya şifre. (Varsayılan: ogretmen / admin123)", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Başarıyla çıkış yaptınız.", "info")
    return redirect(url_for('login'))


# ----------------- Teacher Dashboard -----------------
@app.route('/dashboard')
@login_required
def teacher_dashboard():
    db = get_db()
    cursor = db.cursor()
    user_id = session['user_id']

    # Get teacher's courses
    cursor.execute("""
        SELECT c.*, 
               (SELECT COUNT(*) FROM course_enrollments WHERE course_id = c.id) as student_count,
               (SELECT COUNT(*) FROM attendance_sessions WHERE course_id = c.id) as session_count
        FROM courses c
        WHERE c.teacher_id = ?
        ORDER BY c.code ASC
    """, (user_id,))
    courses = cursor.fetchall()

    # Get recent sessions
    cursor.execute("""
        SELECT s.*, c.code as course_code, c.name as course_name,
               (SELECT COUNT(*) FROM attendance_records WHERE session_id = s.id AND status IN ('PRESENT', 'LATE')) as present_count,
               (SELECT COUNT(*) FROM course_enrollments WHERE course_id = s.course_id) as total_enrolled
        FROM attendance_sessions s
        JOIN courses c ON s.course_id = c.id
        WHERE c.teacher_id = ?
        ORDER BY s.started_at DESC
        LIMIT 8
    """, (user_id,))
    recent_sessions = cursor.fetchall()

    # Overall statistics
    cursor.execute("SELECT COUNT(DISTINCT student_id) FROM course_enrollments ce JOIN courses c ON ce.course_id = c.id WHERE c.teacher_id = ?", (user_id,))
    total_students = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT COUNT(CASE WHEN ar.status = 'PRESENT' THEN 1 END) as present_cnt,
               COUNT(*) as total_records
        FROM attendance_records ar
        JOIN attendance_sessions s ON ar.session_id = s.id
        JOIN courses c ON s.course_id = c.id
        WHERE c.teacher_id = ?
    """, (user_id,))
    stats_row = cursor.fetchone()
    if stats_row and stats_row['total_records'] > 0:
        avg_rate = round((stats_row['present_cnt'] / stats_row['total_records']) * 100, 1)
    else:
        avg_rate = 0.0

    return render_template('teacher_dashboard.html',
                           courses=courses,
                           recent_sessions=recent_sessions,
                           total_students=total_students,
                           avg_rate=avg_rate)


# ----------------- Session Management -----------------
@app.route('/session/start', methods=['POST'])
@login_required
def start_session():
    course_id = request.form.get('course_id')
    title = request.form.get('title', '').strip()
    week_number = request.form.get('week_number', 1, type=int)
    interval = request.form.get('token_interval_seconds', 15, type=int)
    require_loc = 1 if request.form.get('require_location') else 0

    if not course_id or not title:
        flash("Lütfen ders ve oturum başlığını giriniz.", "warning")
        return redirect(url_for('teacher_dashboard'))

    secret_key = uuid.uuid4().hex

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO attendance_sessions (course_id, title, week_number, secret_key, token_interval_seconds, require_location, status, started_at)
        VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE', CURRENT_TIMESTAMP)
    """, (course_id, title, week_number, secret_key, interval, require_loc))
    session_id = cursor.lastrowid
    db.commit()

    flash(f"'{title}' için yoklama oturumu başlatıldı!", "success")
    return redirect(url_for('live_session', session_id=session_id))

@app.route('/session/<int:session_id>/live')
@login_required
def live_session(session_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT s.*, c.code as course_code, c.name as course_name, c.semester, c.academic_year
        FROM attendance_sessions s
        JOIN courses c ON s.course_id = c.id
        WHERE s.id = ?
    """, (session_id,))
    sess = cursor.fetchone()

    if not sess:
        flash("Yoklama oturumu bulunamadı.", "danger")
        return redirect(url_for('teacher_dashboard'))

    # Get enrolled students
    cursor.execute("""
        SELECT st.*, ar.status as attendance_status, ar.scanned_at, ar.method
        FROM students st
        JOIN course_enrollments ce ON st.id = ce.student_id
        LEFT JOIN attendance_records ar ON (st.id = ar.student_id AND ar.session_id = ?)
        WHERE ce.course_id = ?
        ORDER BY st.student_number ASC
    """, (session_id, sess['course_id']))
    roster = cursor.fetchall()

    return render_template('teacher_session.html', session=sess, roster=roster)

@app.route('/session/<int:session_id>/close', methods=['POST'])
@login_required
def close_session(session_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE attendance_sessions
        SET status = 'CLOSED', closed_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (session_id,))
    db.commit()
    flash("Yoklama oturumu başarıyla kapatıldı.", "info")
    return redirect(url_for('live_session', session_id=session_id))

@app.route('/session/<int:session_id>/manual-mark', methods=['POST'])
@login_required
def manual_mark(session_id):
    student_id = request.form.get('student_id', type=int)
    status = request.form.get('status', 'PRESENT') # PRESENT, LATE, EXCUSED, ABSENT

    if not student_id:
        return jsonify({"success": False, "message": "Öğrenci ID belirtilmedi."}), 400

    db = get_db()
    cursor = db.cursor()

    if status == 'ABSENT':
        cursor.execute("DELETE FROM attendance_records WHERE session_id = ? AND student_id = ?", (session_id, student_id))
    else:
        cursor.execute("""
            INSERT INTO attendance_records (session_id, student_id, status, method, scanned_at)
            VALUES (?, ?, ?, 'MANUAL', CURRENT_TIMESTAMP)
            ON CONFLICT(session_id, student_id) DO UPDATE SET
                status = excluded.status,
                method = 'MANUAL',
                scanned_at = CURRENT_TIMESTAMP
        """, (session_id, student_id, status))

    db.commit()
    return jsonify({"success": True, "student_id": student_id, "status": status})


# ----------------- Real-time APIs for Projection Screen -----------------
@app.route('/api/session/<int:session_id>/token')
def api_session_token(session_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM attendance_sessions WHERE id = ?", (session_id,))
    sess = cursor.fetchone()

    if not sess:
        return jsonify({"error": "Session not found"}), 404

    if sess['status'] != 'ACTIVE':
        return jsonify({"status": "CLOSED", "message": "Yoklama oturumu kapalı."})

    # Automatically detect whether running on localhost, local Wi-Fi IP, or public domain/tunnel
    proto = request.headers.get('X-Forwarded-Proto', request.scheme)
    host = request.headers.get('X-Forwarded-Host', request.host)
    base_url = f"{proto}://{host}"

    token_info = get_current_token_info(
        secret_key=sess['secret_key'],
        session_id=session_id,
        interval_seconds=sess['token_interval_seconds'],
        base_url=base_url
    )
    token_info['session_status'] = 'ACTIVE'
    return jsonify(token_info)

@app.route('/api/session/<int:session_id>/status')
def api_session_status(session_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT course_id, status FROM attendance_sessions WHERE id = ?", (session_id,))
    sess = cursor.fetchone()
    if not sess:
        return jsonify({"error": "Session not found"}), 404

    # Enrolled count
    cursor.execute("SELECT COUNT(*) FROM course_enrollments WHERE course_id = ?", (sess['course_id'],))
    total_enrolled = cursor.fetchone()[0]

    # Present students list with latest scan times
    cursor.execute("""
        SELECT st.id, st.student_number, st.full_name, ar.status, ar.scanned_at, ar.method
        FROM attendance_records ar
        JOIN students st ON ar.student_id = st.id
        WHERE ar.session_id = ?
        ORDER BY ar.scanned_at DESC
    """, (session_id,))
    records = [dict(row) for row in cursor.fetchall()]

    present_count = len([r for r in records if r['status'] in ('PRESENT', 'LATE')])
    percentage = round((present_count / total_enrolled * 100), 1) if total_enrolled > 0 else 0

    return jsonify({
        "session_id": session_id,
        "status": sess['status'],
        "total_enrolled": total_enrolled,
        "present_count": present_count,
        "attendance_percentage": percentage,
        "records": records
    })


# ----------------- Student Attendance Check-in -----------------
@app.route('/attend')
def attend_page():
    session_id = request.args.get('session_id', type=int)
    token = request.args.get('token', '').strip()

    session_info = None
    if session_id:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT s.*, c.code as course_code, c.name as course_name, u.full_name as teacher_name
            FROM attendance_sessions s
            JOIN courses c ON s.course_id = c.id
            LEFT JOIN users u ON c.teacher_id = u.id
            WHERE s.id = ?
        """, (session_id,))
        session_info = cursor.fetchone()

    return render_template('student_attend.html',
                           session_id=session_id,
                           token=token,
                           session_info=session_info)

@app.route('/student/scan')
def student_scan():
    """In-browser camera scanner page for smartphones."""
    return render_template('student_scan.html')

@app.route('/api/attend/submit', methods=['POST'])
def attend_submit():
    if request.is_json:
        data = request.get_json() or {}
        raw_session_id = data.get('session_id')
        token = str(data.get('token', '')).strip()
        student_number = str(data.get('student_number', '')).strip()
    else:
        raw_session_id = request.form.get('session_id')
        token = request.form.get('token', '').strip()
        student_number = request.form.get('student_number', '').strip()

    try:
        session_id = int(raw_session_id) if raw_session_id is not None else None
    except (ValueError, TypeError):
        session_id = None

    user_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')[:250]

    if not session_id or not token or not student_number:
        return jsonify({
            "success": False,
            "message": "Eksik bilgi: Öğrenci numarası, oturum ve QR kod bilgisi gereklidir."
        }), 400

    db = get_db()
    cursor = db.cursor()

    # 1. Fetch Session
    cursor.execute("""
        SELECT s.*, c.code as course_code, c.name as course_name
        FROM attendance_sessions s
        JOIN courses c ON s.course_id = c.id
        WHERE s.id = ?
    """, (session_id,))
    sess = cursor.fetchone()

    if not sess:
        return jsonify({"success": False, "message": "Geçersiz oturum numarası."}), 404

    if sess['status'] != 'ACTIVE':
        return jsonify({
            "success": False,
            "message": "Bu yoklama oturumu kapatılmıştır. Yeni giriş kabul edilmemektedir."
        }), 400

    # 2. Verify Dynamic QR Token
    is_valid = verify_token(
        secret_key=sess['secret_key'],
        session_id=session_id,
        candidate_token=token,
        interval_seconds=sess['token_interval_seconds'],
        tolerance_windows=2
    )

    if not is_valid:
        return jsonify({
            "success": False,
            "message": "QR kodun süresi doldu veya geçersiz! Lütfen tahtadaki güncel QR kodu tekrar okutun."
        }), 400

    # 3. Verify Student exists & is enrolled
    cursor.execute("SELECT * FROM students WHERE student_number = ?", (student_number,))
    student = cursor.fetchone()

    if not student:
        return jsonify({
            "success": False,
            "message": f"{student_number} numaralı öğrenci sistemde bulunamadı. Lütfen öğrenci işleri / hocanızla iletişime geçin."
        }), 404

    cursor.execute("SELECT * FROM course_enrollments WHERE course_id = ? AND student_id = ?",
                   (sess['course_id'], student['id']))
    enrollment = cursor.fetchone()

    if not enrollment:
        return jsonify({
            "success": False,
            "message": f"{student['full_name']} ({student_number}), bu derse kayıtlı görünmüyor."
        }), 403

    # 4. Duplicate Check
    cursor.execute("SELECT * FROM attendance_records WHERE session_id = ? AND student_id = ?",
                   (session_id, student['id']))
    existing = cursor.fetchone()

    if existing:
        return jsonify({
            "success": True,
            "already_recorded": True,
            "message": f"Sayın {student['full_name']}, yoklamanız daha önce saat {existing['scanned_at']} itibarıyla zaten kaydedilmiş!",
            "student_name": student['full_name'],
            "student_number": student['student_number'],
            "course": f"{sess['course_code']} - {sess['course_name']}",
            "scanned_at": existing['scanned_at']
        })

    # 5. Insert Attendance Record
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        INSERT INTO attendance_records (session_id, student_id, status, method, scanned_at, ip_address, user_agent)
        VALUES (?, ?, 'PRESENT', 'QR', ?, ?, ?)
    """, (session_id, student['id'], now_str, user_ip, user_agent))
    db.commit()

    return jsonify({
        "success": True,
        "already_recorded": False,
        "message": f"Tebrikler {student['full_name']}! Yoklamanız başarıyla alındı.",
        "student_name": student['full_name'],
        "student_number": student['student_number'],
        "course": f"{sess['course_code']} - {sess['course_name']}",
        "scanned_at": now_str
    })


# ----------------- Reports & Analytics -----------------
@app.route('/reports')
@login_required
def reports():
    db = get_db()
    cursor = db.cursor()
    user_id = session['user_id']
    course_id = request.args.get('course_id', type=int)

    # Get teacher's courses for dropdown
    cursor.execute("SELECT id, code, name FROM courses WHERE teacher_id = ? ORDER BY code", (user_id,))
    courses = cursor.fetchall()

    selected_course = None
    sessions_list = []
    student_summary = []

    if courses:
        if not course_id:
            course_id = courses[0]['id']

        cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
        selected_course = cursor.fetchone()

        # Get all sessions for this course
        cursor.execute("""
            SELECT s.*,
                   (SELECT COUNT(*) FROM attendance_records WHERE session_id = s.id AND status IN ('PRESENT', 'LATE')) as present_cnt,
                   (SELECT COUNT(*) FROM course_enrollments WHERE course_id = s.course_id) as total_students
            FROM attendance_sessions s
            WHERE s.course_id = ?
            ORDER BY s.started_at DESC
        """, (course_id,))
        sessions_list = cursor.fetchall()

        # Student cumulative attendance breakdown
        total_course_sessions = len(sessions_list)
        cursor.execute("""
            SELECT st.id, st.student_number, st.full_name, st.department,
                   COUNT(CASE WHEN ar.status = 'PRESENT' THEN 1 END) as present_count,
                   COUNT(CASE WHEN ar.status = 'LATE' THEN 1 END) as late_count,
                   COUNT(CASE WHEN ar.status = 'EXCUSED' THEN 1 END) as excused_count
            FROM students st
            JOIN course_enrollments ce ON st.id = ce.student_id
            LEFT JOIN attendance_sessions s ON s.course_id = ce.course_id
            LEFT JOIN attendance_records ar ON (ar.session_id = s.id AND ar.student_id = st.id)
            WHERE ce.course_id = ?
            GROUP BY st.id
            ORDER BY st.student_number ASC
        """, (course_id,))
        student_rows = cursor.fetchall()

        for s in student_rows:
            attended = s['present_count'] + s['late_count']
            rate = round((attended / total_course_sessions * 100), 1) if total_course_sessions > 0 else 0
            student_summary.append({
                'id': s['id'],
                'student_number': s['student_number'],
                'full_name': s['full_name'],
                'department': s['department'],
                'present_count': s['present_count'],
                'late_count': s['late_count'],
                'excused_count': s['excused_count'],
                'attendance_rate': rate,
                'total_sessions': total_course_sessions
            })

    return render_template('reports.html',
                           courses=courses,
                           selected_course=selected_course,
                           sessions=sessions_list,
                           student_summary=student_summary)

@app.route('/reports/session/<int:session_id>/export')
@login_required
def export_session_csv(session_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT s.*, c.code as course_code, c.name as course_name
        FROM attendance_sessions s
        JOIN courses c ON s.course_id = c.id
        WHERE s.id = ?
    """, (session_id,))
    sess = cursor.fetchone()

    if not sess:
        flash("Oturum bulunamadı.", "danger")
        return redirect(url_for('reports'))

    cursor.execute("""
        SELECT st.student_number, st.full_name, st.department,
               COALESCE(ar.status, 'ABSENT') as status,
               ar.scanned_at, ar.method, ar.ip_address
        FROM students st
        JOIN course_enrollments ce ON st.id = ce.student_id
        LEFT JOIN attendance_records ar ON (st.id = ar.student_id AND ar.session_id = ?)
        WHERE ce.course_id = ?
        ORDER BY st.student_number ASC
    """, (session_id, sess['course_id']))
    records = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(['Öğrenci No', 'Ad Soyad', 'Bölüm', 'Durum', 'Katılım Zamanı', 'Yöntem', 'IP Adresi'])

    status_tr = {
        'PRESENT': 'Mevcut (Var)',
        'LATE': 'Geç Kaldı',
        'EXCUSED': 'İzinli / Raporlu',
        'ABSENT': 'Yok'
    }

    for r in records:
        writer.writerow([
            r['student_number'],
            r['full_name'],
            r['department'],
            status_tr.get(r['status'], r['status']),
            r['scanned_at'] or '-',
            r['method'] or '-',
            r['ip_address'] or '-'
        ])

    csv_data = output.getvalue().encode('utf-8-sig') # utf-8 with BOM for Excel compatibility in Turkish
    filename = f"Yoklama_{sess['course_code']}_Hafta_{sess['week_number']}.csv"

    response = make_response(csv_data)
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    response.headers['Content-type'] = 'text/csv; charset=utf-8'
    return response

# ----------------- Student Roster Management -----------------
@app.route('/students')
@login_required
def student_roster():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT st.*, 
               (SELECT COUNT(*) FROM course_enrollments WHERE student_id = st.id) as enrolled_course_count
        FROM students st
        ORDER BY st.student_number ASC
    """)
    students = cursor.fetchall()
    return render_template('students.html', students=students)

if __name__ == '__main__':
    init_db(seed=True)
    server_ip = get_server_ip()
    print("=" * 65)
    print("🚀 QR KOD TABANLI SINIF YOKLAMA SİSTEMİ BAŞLATILIYOR")
    print(f"👉 Yerel Erişim (Localhost) : http://localhost:5000")
    print(f"📱 Telefon/Ağ Erişimi (Wi-Fi): http://{server_ip}:5000")
    print(f"🔑 Varsayılan Öğretmen Girişi: Kullanıcı Adı: ogretmen | Şifre: admin123")
    print("=" * 65)
    app.run(host='0.0.0.0', port=5000, debug=True)
