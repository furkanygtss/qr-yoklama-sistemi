"""
Security and Dynamic QR Code Token Service.
Implements time-window HMAC dynamic tokens and QR code image generation.
"""
import hmac
import hashlib
import time
import io
import base64
import socket
import qrcode
from PIL import Image

def get_server_ip():
    """Detects primary local network IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

def generate_window_token(secret_key: str, session_id: int, interval_seconds: int = 15, offset: int = 0) -> str:
    """
    Generates a 16-character HMAC token for a specific time window.
    offset=0: current window
    offset=-1: previous window (grace period)
    """
    now = int(time.time())
    window_idx = (now // interval_seconds) + offset
    message = f"{session_id}:{window_idx}".encode('utf-8')
    token = hmac.new(secret_key.encode('utf-8'), message, hashlib.sha256).hexdigest()[:16]
    return token

def get_current_token_info(secret_key: str, session_id: int, interval_seconds: int = 15, base_url: str = None):
    """
    Returns current token, time remaining in seconds, and QR code data URL.
    """
    now = int(time.time())
    window_idx = now // interval_seconds
    seconds_remaining = interval_seconds - (now % interval_seconds)
    token = generate_window_token(secret_key, session_id, interval_seconds, offset=0)

    if not base_url:
        server_ip = get_server_ip()
        base_url = f"http://{server_ip}:5000"

    # Direct attendance URL embedded in the QR
    attendance_url = f"{base_url}/attend?session_id={session_id}&token={token}"

    # Generate QR Code image in memory
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(attendance_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1E293B", back_color="#FFFFFF")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return {
        "session_id": session_id,
        "token": token,
        "seconds_remaining": seconds_remaining,
        "total_interval": interval_seconds,
        "attendance_url": attendance_url,
        "qr_base64": f"data:image/png;base64,{qr_base64}"
    }

def verify_token(secret_key: str, session_id: int, candidate_token: str, interval_seconds: int = 15, tolerance_windows: int = 2) -> bool:
    """
    Verifies candidate token against current and recent past windows.
    tolerance_windows=2 allows current window, -1 window, and -2 window (e.g. up to 30-45s)
    to prevent race conditions while students are loading page.
    """
    if not candidate_token or not secret_key:
        return False

    candidate_token = candidate_token.strip().lower()

    for offset in range(0, -tolerance_windows - 1, -1):
        expected_token = generate_window_token(secret_key, session_id, interval_seconds, offset=offset)
        if hmac.compare_digest(candidate_token, expected_token.lower()):
            return True

    return False
