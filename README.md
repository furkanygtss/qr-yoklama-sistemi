# 📱 Dinamik QR Kod Tabanlı Akıllı Sınıf Yoklama Sistemi

Bu proje; üniversitelerde, okullarda ve eğitim kurumlarında kağıt imza listesiyle yoklama alma devrini kapatıp, tahtada her **15 saniyede bir kriptografik olarak yenilenen dinamik QR kodlar** üreterek öğrencilerin akıllı telefonlarıyla tek dokunuşta sınıf mevcudunu kaydeden modern bir web otomasyon sistemidir.

Proje, **Kalıcı 7/24 Ücretsiz Bulut Dağıtımı (Render.com & Gunicorn)** mimarisiyle dünyanın her yerinden kesintisiz erişilecek şekilde yapılandırılmıştır.

---

## 🌟 Öne Çıkan Özellikler

1. **Dinamik TOTP Tabanlı QR Güvenliği (Hile Önleme)**:
   - Statik QR kodların aksine, QR içerisindeki token **HMAC-SHA256** algoritması ile her 15 saniyede bir otomatik döner.
   - Sınıftaki bir öğrenci tahtadaki QR'ın fotoğrafını çekip WhatsApp/Telegram'dan derse gelmeyen arkadaşına gönderse dahi, kodun süresi dolacağı için sistem geçersiz sayar.
2. **Sıfır Kurulum / Web-First Mimari**:
   - Öğrencilerin telefonlarına herhangi bir mobil uygulama (.apk / App Store) indirmesine gerek yoktur.
   - Standart telefon kamerası (iOS Camera / Google Lens) veya yerleşik **HTML5 Kamera Okuyucu** (`/student/scan`) üzerinden tarayıcıda doğrudan çalışır.
3. **Öğretmen Canlı Projeksiyon Paneli**:
   - Büyük sınıf projeksiyonları için tasarlanmış canlı izleme ekranı (`/session/<id>/live`).
   - Geri sayım çubuğu, anlık sınıf katılım oranı göstergesi (`1 / 5 Katıldı, %20`), sesli bildirim (Web Audio chime) ve milisaniyelik canlı akış.
   - Telefonu olmayan veya şarjı biten öğrenciler için tek tıkla **manuel yoklama düzeltme** (Var / Geç / İzinli / Yok).
4. **Mükerrer Kayıt Engeli**:
   - Bir öğrenci aynı oturumda birden fazla kez yoklama veremez (`UNIQUE(session_id, student_id)` veritabanı kısıtı).
5. **Raporlama ve Excel / CSV Dışa Aktarımı**:
   - Dönemlik ders bazında öğrenci devamlılık yüzdeleri (%70 devam kuralı takibi).
   - Tek tıkla Türkçe karakter destekli UTF-8 BOM CSV / Excel listesi indirme.

---

## 🏗️ Sistem Mimarisi & Teknoloji Yığını

- **Backend**: Python 3.14 + Flask 3.1.3
- **Üretim Sunucusu (Production WSGI)**: Gunicorn 23.x
- **Veritabanı**: SQLite3 (İlişkisel şema, ACID uyumlu, Foreign Key destekli)
- **Kriptografi & QR Motoru**: HMAC-SHA256, Python `qrcode`, `Pillow`
- **Frontend**: Tailwind CSS (CDN), FontAwesome 6 Icons, HTML5-QRCode
- **Bulut Dağıtımı**: Render.com (7/24 Kalıcı Ücretsiz Web Servisi)

---

## 🌐 Kalıcı 7/24 Ücretsiz Bulut Dağıtımı (Render.com)

Sistem, bilgisayarınız kapalıyken bile 7/24 internette yayında kalacak şekilde **Render.com** ve **Gunicorn** ile tam entegre çalışır.

### Yapılandırma Dosyaları:
* `render.yaml`: Render bulut altyapısı için tek tıkla kurulum tanımları.
* `Procfile`: `web: gunicorn wsgi:app` komutu ile üretim sunucusunu başlatır.
* `wsgi.py`: Veritabanını otomatik başlatan ve Flask uygulamasını servis eden giriş noktası.
* `requirements.txt`: Gunicorn ve gerekli tüm kütüphaneler.

### Canlıya Alma Adımları:
1. Deponuz GitHub'a bağlandığında Render otomatik olarak algılar.
2. **Build Command:** `pip install -r requirements.txt`
3. **Start Command:** `gunicorn wsgi:app`
4. Render size ömür boyu ücretsiz, SSL sertifikalı (HTTPS) kalıcı bir web adresi verir (Örn: `https://qr-yoklama-sistemi.onrender.com`).

---

## 👨‍🏫 Tanımlı Öğretmen ve Sınıf Mevcudu

### Öğretmen:
* **Öğretmen:** Ahmet Deniz
* **Kullanıcı Adı:** `ahmetdeniz` *(veya `ogretmen`)*
* **Şifre:** `admin123`

### Sınıf Mevcudu (5 Öğrenci):
* `252302034` - **Furkan Yiğit Koygun**
* `252302035` - **Ahmet Yılmaz**
* `252302036` - **Mehmet Kaya**
* `252302037` - **Zeynep Demir**
* `252302038` - **Ali Çelik**

---

## 🧪 Otomatik Testleri Koşturma

Sistemde bulunan 6 farklı birim ve entegrasyon testini çalıştırmak için:
```bash
python test_app.py
```
*(6/6 test başarıyla geçmektedir).*
