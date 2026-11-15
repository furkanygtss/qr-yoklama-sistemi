# 📱 Dinamik QR Kod Tabanlı Akıllı Sınıf Yoklama Sistemi

Bu proje; üniversitelerde, okullarda ve eğitim kurumlarında **kağıt imza listesiyle yoklama alma** devrini kapatıp, projeksiyon tahtasında her **15 saniyede bir kriptografik olarak yenilenen dinamik QR kodlar** üreterek öğrencilerin akıllı telefonlarıyla tek dokunuşta sınıf mevcudunu kaydeden modern bir web otomasyon sistemidir.

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
   - Geri sayım çubuğu, anlık sınıf katılım oranı göstergesi (`21/25 Katıldı, %84`), sesli bildirim (Web Audio chime) ve milisaniyelik canlı akış.
   - Telefonu olmayan veya şarjı biten öğrenciler için tek tıkla **manuel yoklama düzeltme** (Var / Geç / İzinli / Yok).
4. **Mükerrer Kayıt Engeli**:
   - Bir öğrenci aynı oturumda birden fazla kez yoklama veremez (`UNIQUE(session_id, student_id)` veritabanı kısıtı).
5. **Raporlama ve Excel / CSV Dışa Aktarımı**:
   - Dönemlik ders bazında öğrenci devamlılık yüzdeleri (%70 devam kuralı takibi).
   - Tek tıkla Türkçe karakter destekli UTF-8 BOM CSV / Excel listesi indirme.

---

## 🏗️ Sistem Mimarisi & Teknoloji Yığını

- **Backend**: Python 3.14 + Flask 3.1.3
- **Veritabanı**: SQLite3 (İlişkisel şema, ACID uyumlu, Foreign Key destekli)
- **Kriptografi & QR Motoru**: HMAC-SHA256, Python `qrcode`, `Pillow`
- **Frontend**: Tailwind CSS (CDN), FontAwesome 6 Icons, HTML5-QRCode
- **Raporlama**: Python-docx (Otomatik oluşturulan teknik şartname ve çalışma kılavuzu)

---

## 🚀 Hızlı Başlangıç ve Çalıştırma

### 1. Gereksinimleri Yükleyin
```bash
pip install -r requirements.txt
```

### 2. Uygulama Sunucusunu Başlatın
```bash
python app.py
```

Sunucu başladığında terminalde şu bilgileri göreceksiniz:
```text
=================================================================
🚀 QR KOD TABANLI SINIF YOKLAMA SİSTEMİ BAŞLATILIYOR
👉 Yerel Erişim (Localhost) : http://localhost:5000
📱 Telefon/Ağ Erişimi (Wi-Fi): http://192.168.1.113:5000
🔑 Varsayılan Öğretmen Girişi: Kullanıcı Adı: ogretmen | Şifre: admin123
=================================================================
```

### 3. Tarayıcınızdan Giriş Yapın
- **Öğretmen Paneli**: `http://localhost:5000` (Kullanıcı: `ogretmen`, Şifre: `admin123`)
- **Öğrenci Doğrudan Giriş**: `http://192.168.1.113:5000/attend`
- **Öğrenci Kamera Tarayıcısı**: `http://192.168.1.113:5000/student/scan`

---

## 🧪 Otomatik Testleri Koşturma

Sistemde bulunan 6 farklı birim ve entegrasyon testini (giriş, oturum başlatma, dinamik token doğrulama, duplicate check, invalid token reddi, CSV export) çalıştırmak için:
```bash
python test_app.py
```

---

## 📄 Oluşturulan .DOCX Raporu

Proje klasöründe sistemin nasıl çalıştığını, matematiksel modelini, veritabanı şemasını ve ekranlarını detaylandıran kapsamlı bir Word raporu üretilmiştir:
- **Dosya Adı**: `QR_Yoklama_Sistemi_Raporu.docx`
- **İçerik Başlıkları**:
  1. Yönetici Özeti ve Proje Amacı
  2. Sistem Mimarisi ve Teknoloji Yığını
  3. QR Kod Tabanlı Yoklama Mekanizması ve Hile Önleme
  4. Veritabanı Tasarımı ve Veri Modeli
  5. Kullanıcı Rolleri ve Uçtan Uca İş Akışları
  6. REST API Uç Noktaları ve Entegrasyon
  7. Güvenlik, Sahteciliği Önleme ve Kıyaslama Analizi
  8. Kurulum, Yapılandırma ve Çalıştırma Kılavuzu
  9. Gelecek Geliştirmeler ve Yol Haritası
  10. Sonuç

Raporu yeniden derlemek isterseniz:
```bash
python generate_report.py
```

---

## 👨‍💻 Örnek Test Öğrenci Numaraları
Sistem veritabanına otomatik olarak 25 adet gerçekçi öğrenci kaydı yüklenmiştir. Test için kullanabileceğiniz bazı numaralar:
- `202301001` - Zeynep Kaya
- `202301002` - Mehmet Can Demir
- `202301003` - Ayşe Nur Çelik
- `202301004` - Emre Şahin
- `202301005` - Elif Yıldırım
