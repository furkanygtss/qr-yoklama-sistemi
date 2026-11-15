"""
Tek Tıkla Canlı Web Sitesi ve Sunum Başlatıcı (Online Presentation Launcher).
Flask sunucusunu ve Cloudflare tünelini eşzamanlı başlatır,
tüm dünyaya açık, ücretsiz ve güvenli (HTTPS) canlı bir web sitesi adresi üretir.
"""

import sys
import os
import subprocess
import re
import time
import threading
import webbrowser
from database import init_db

def start_flask():
    from app import app
    # Suppress verbose flask output in the main console
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

def copy_to_clipboard(text):
    try:
        if sys.platform == 'win32':
            subprocess.run(['clip.exe'], input=text.strip().encode('utf-8'), check=True)
    except Exception:
        pass

def main():
    print("=" * 75)
    print("🚀 AKILLI SINIF YOKLAMA SİSTEMİ - CANLI WEB SİTESİ VE SUNUM BAŞLATICI")
    print("=" * 75)
    print("1. Veritabanı ve tohum kayıtlar doğrulanıyor...")
    init_db(seed=True)

    print("2. Flask sunucusu arka planda başlatılıyor (Port: 5000)...")
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    time.sleep(1.5)

    cloudflared_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cloudflared.exe')
    if not os.path.exists(cloudflared_path):
        print(f"HATA: {cloudflared_path} bulunamadı!")
        return

    print("3. Ücretsiz Cloudflare HTTPS tüneli açılıyor...")
    cmd = [cloudflared_path, "tunnel", "--url", "http://127.0.0.1:5000"]
    
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding='utf-8',
        errors='ignore'
    )

    public_url = None
    url_pattern = re.compile(r'https://[a-zA-Z0-9\-]+\.trycloudflare\.com')

    # Monitor output for the tunnel URL
    for line in iter(proc.stdout.readline, ''):
        match = url_pattern.search(line)
        if match:
            public_url = match.group(0)
            break
        if "Registered tunnel connection" in line:
            break

    if not public_url:
        print("Tünel adresi aranıyor, lütfen 3 saniye bekleyin...")
        time.sleep(3)

    if public_url:
        copy_to_clipboard(public_url)
        print("\n" + "🌟" * 38)
        print("🎉 TEBRİKLER! CANLI WEB SİTENİZ VE SUNUM BAĞLANTINIZ HAZIR!")
        print("🌟" * 38)
        print(f"\n🌐 CANLI WEB SİTESİ ADRESİNİZ (DÜNYANIN HER YERİNDEN ERİŞİLEBİLİR):")
        print(f"👉  {public_url}")
        print("    (Bağlantı otomatik olarak panoya/clipboard kopyalandı!)\n")
        print("-" * 75)
        print("📌 HOCAYA SUNUM İÇİN HIZLI BAĞLANTILAR:")
        print(f"👨‍🏫 Öğretmen Paneli Girişi : {public_url}/login")
        print(f"   (Varsayılan Giriş: ogretmen / admin123)")
        print(f"📱 Öğrenci Yoklama Ekranı: {public_url}/attend")
        print(f"📸 Kamera ile QR Okuyucu  : {public_url}/student/scan")
        print("-" * 75)
        print("\n💡 SUNUM İPUCU:")
        print("1. Projeksiyonda Öğretmen Paneline girip 'Yoklama Başlat' deyin.")
        print("2. Hocanıza: 'Hocam, telefonunuzun kamerasını tahtadaki QR koda tutun' deyin.")
        print("3. Hoca QR'ı okuttuğu anda hocanın telefonunda web sayfası açılacak!")
        print("4. Hoca öğrenci numarasını girip butona basınca projeksiyonda anında")
        print("   yeşil onay işareti çıkacak ve ses çalacak!\n")
        print("=" * 75)
        print("⚠️  Sunumu bitirene kadar bu pencereyi KAPATMAYINIZ.")
        print("    Durdurmak için klavyeden Ctrl + C tuşlarına basabilirsiniz.")
        print("=" * 75)

        # Open in default browser
        webbrowser.open(f"{public_url}/login")

        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nSunum oturumu sonlandırılıyor...")
            proc.terminate()
            print("Kapatıldı. Başarılar dileriz!")
    else:
        print("Tünel URL'i yakalanamadı. Lütfen internet bağlantınızı kontrol ediniz.")
        proc.terminate()

if __name__ == '__main__':
    main()
