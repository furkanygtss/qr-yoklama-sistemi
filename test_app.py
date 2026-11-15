"""
Comprehensive test script for the QR Attendance System.
Tests authentication, dynamic token generation, live API, attendance check-in, duplicate prevention, and reports.
"""
import unittest
from app import app
from database import init_db, get_db
from token_service import generate_window_token, verify_token

class QRAttendanceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db(seed=True)
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        cls.client = app.test_client()

    def test_01_login_page_renders(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ogretmen', response.data)

    def test_02_teacher_login_success(self):
        response = self.client.post('/login', data={
            'username': 'ogretmen',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Prof. Dr. Ahmet Yılmaz'.encode('utf-8'), response.data)

    def test_03_dashboard_loads(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'ogretmen'
            sess['full_name'] = 'Prof. Dr. Ahmet Yılmaz'
            sess['role'] = 'teacher'

        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'YAZ401', response.data)

    def test_04_token_generation_and_verification(self):
        secret = "test_secret_key"
        session_id = 99
        token = generate_window_token(secret, session_id, interval_seconds=15, offset=0)
        self.assertTrue(verify_token(secret, session_id, token, interval_seconds=15))
        self.assertFalse(verify_token(secret, session_id, "invalid_token_123", interval_seconds=15))

    def test_05_start_session_and_token_api(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'ogretmen'
            sess['full_name'] = 'Prof. Dr. Ahmet Yılmaz'
            sess['role'] = 'teacher'

        # Start a new test session
        response = self.client.post('/session/start', data={
            'course_id': 1,
            'title': 'Test Hafta 4 - Yoklama Testi',
            'week_number': 4,
            'token_interval_seconds': 15
        }, follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        # Get the new session ID
        db = get_db()
        sess_row = db.execute("SELECT id, secret_key FROM attendance_sessions ORDER BY id DESC LIMIT 1").fetchone()
        session_id = sess_row['id']
        secret_key = sess_row['secret_key']

        # Call token API
        token_res = self.client.get(f'/api/session/{session_id}/token')
        self.assertEqual(token_res.status_code, 200)
        token_data = token_res.get_json()
        self.assertIn('token', token_data)
        self.assertIn('qr_base64', token_data)
        self.assertEqual(token_data['session_status'], 'ACTIVE')

        # Test valid student attendance
        active_token = token_data['token']
        attend_res = self.client.post('/api/attend/submit', json={
            'session_id': session_id,
            'token': active_token,
            'student_number': '202301001'
        })
        self.assertEqual(attend_res.status_code, 200)
        attend_data = attend_res.get_json()
        self.assertTrue(attend_data['success'])
        self.assertFalse(attend_data['already_recorded'])
        self.assertEqual(attend_data['student_name'], 'Zeynep Kaya')

        # Test duplicate attendance check
        dup_res = self.client.post('/api/attend/submit', json={
            'session_id': session_id,
            'token': active_token,
            'student_number': '202301001'
        })
        self.assertEqual(dup_res.status_code, 200)
        dup_data = dup_res.get_json()
        self.assertTrue(dup_data['success'])
        self.assertTrue(dup_data['already_recorded'])

        # Test expired/invalid token
        invalid_res = self.client.post('/api/attend/submit', json={
            'session_id': session_id,
            'token': 'fake_expired_token',
            'student_number': '202301002'
        })
        self.assertEqual(invalid_res.status_code, 400)
        self.assertFalse(invalid_res.get_json()['success'])

        # Test session status API
        status_res = self.client.get(f'/api/session/{session_id}/status')
        self.assertEqual(status_res.status_code, 200)
        status_data = status_res.get_json()
        self.assertGreaterEqual(status_data['present_count'], 1)

    def test_06_reports_and_csv_export(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'ogretmen'
            sess['full_name'] = 'Prof. Dr. Ahmet Yılmaz'
            sess['role'] = 'teacher'

        rep_res = self.client.get('/reports')
        self.assertEqual(rep_res.status_code, 200)

        csv_res = self.client.get('/reports/session/1/export')
        self.assertEqual(csv_res.status_code, 200)
        self.assertIn('text/csv', csv_res.headers['Content-Type'])
        self.assertIn('Zeynep Kaya'.encode('utf-8'), csv_res.data)

if __name__ == '__main__':
    unittest.main()
