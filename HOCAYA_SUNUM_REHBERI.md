# 🎓 HOCAYA SUNUM REHBERİ & CANLI DEMO SENARYOSU

Bu rehber, geliştirdiğiniz **Dinamik QR Kod Tabanlı Akıllı Sınıf Yoklama Sistemi**'ni dersin hocasına sunarken tam not almanız için hazırlanmış adım adım sunum kılavuzudur.

Sistem **Kalıcı 7/24 Ücretsiz Bulut Dağıtımı (Render.com)** üzerinde çalışmakta olup, bilgisayarınızdan bağımsız olarak doğrudan canlı web sitesi üzerinden sunulabilir.

---

## ⚡ 1. Sunum Öncesi 10 Saniyelik Hazırlık

1. Tarayıcınızda canlı bulut web sitesi adresinizi açın:
   👉 **`https://qr-yoklama-sistemi.onrender.com`** *(veya oluşturduğunuz Render linki)*
2. Öğretmen girişi yapın:
   * **Öğretmen:** Ahmet Deniz
   * **Kullanıcı Adı:** `ahmetdeniz` *(veya `ogretmen`)*
   * **Şifre:** `admin123`
3. Projeksiyonu bağlayın veya ekran paylaşımını başlatın.

---

## 🎬 2. Hocayı Etkileyecek 5 Dakikalık Canlı Demo Akışı

### Adım 1: Giriş ve Problemi Tanımlama (1 Dakika)
> *"Hocam, günümüzde 50-100 kişilik sınıflarda kağıt dolaştırarak yoklama almak hem en az 10-15 dakika ders kaybına yol açıyor, hem de öğrencilerin derste olmayan arkadaşları yerine imza atmasını engelleyemiyor. Basit statik QR kodlar ise fotoğrafı çekilip WhatsApp'tan paylaşılabildiği için hileye çok açık.*  
> *Biz bu problemi çözmek için; bankacılık standartlarında **Dinamik TOTP (Zaman Ayarlı) QR Kod** üreten, öğrencilerin uygulama indirmesine gerek kalmadan saniyeler içinde yoklama veren ve bulutta 7/24 kesintisiz çalışan akıllı bir sınıf sistemi geliştirdik."*

### Adım 2: Canlı Yoklama Başlatma & Projeksiyon Ekranı (1 Dakika)
* Ekranda sorumlu olduğunuz derslerden birini seçin (Örn: **YAZ401 - Yazılım Mimarisi ve Tasarımı**).
* **"Yoklama Başlat"** butonuna basın. Konu başlığı olarak *"Hafta 4 - Tasarım Desenleri"* yazıp başlatın.
* Sağ üstteki **"Tam Ekran"** butonuna basarak projeksiyonu dev ekrana alın.
* Tahtada dönen 15 saniyelik geri sayım çubuğunu ve şifrelenmiş dinamik QR kodu gösterin.

### Adım 3: İnteraktif Katılım (Hocaya Telefonunu Kullandırtın!) ⭐⭐⭐
> *"Hocam, sistemin pratikliğini canlı test etmek için lütfen telefonunuzun kamerasını tahtadaki QR koda doğru tutabilir misiniz?"*
* Hoca telefon kamerasını tahtaya tuttuğu anda telefonunun ekranında doğrudan web sitesi bağlantısı belirecektir.
* Hoca bağlantıya tıkladığında öğrenci yoklama ekranı açılır.
* Hocaya kendi öğrenci numaranızı söyleyin: **`252302034` (Furkan Yiğit Koygun)**.
* Hoca numarayı girip **"Yoklamaya Katıl"** butonuna bastığı anda:
  1. **Tahtada sesli bir zil (ding sesi) çalacak!**
  2. Sağ taraftaki canlı akışta anında **Furkan Yiğit Koygun - 252302034 (QR ile Okutuldu - 14:05)** yeşil onay işaretiyle belirecek.
  3. Sınıf mevcudu ibresi **`1 / 5 (%20)`** olarak dolacaktır!

### Adım 4: Hile Önleme Testi (Jürinin En Çok Sevdiği Kısım!)
> *"Hocam, peki bir öğrenci bu QR'ın fotoğrafını çekip sınıfta olmayan arkadaşına gönderirse ne olur?"*
* Tahtadaki geri sayımı gösterin: QR kod her 15 saniyede bir **HMAC-SHA256** ile şifrelenerek değişmektedir.
* Arkadaşına fotoğraf gidene kadar kodun süresi dolacağı için sunucu isteği reddedecek ve ekranda **"QR Kodun süresi doldu! Tahtadaki güncel kodu okutun"** uyarısı çıkacaktır.

### Adım 5: Mükerrer (Çift) Kayıt ve Manuel İstisna Yönetimi
* Hocaya aynı öğrenci numarasını tekrar göndermesini rica edin:
  * Sistem anında **"Sayın Furkan Yiğit Koygun, yoklamanız daha önce zaten alınmıştır!"** uyarısını verir.
* *"Peki hocam, bir öğrencinin şarjı biterse ne yapıyoruz?"* sorusunu kendiniz sorup yanıtlayın:
  * Tahtada **"Tüm Sınıf"** sekmesine geçin. Listeden diğer öğrencilerin (Örn: **Ahmet Yılmaz - 252302035** veya **Mehmet Kaya - 252302036**) yanındaki **"Var"** veya **"Geç"** butonuna tek tıkla basarak manuel olarak işaretleyin.

### Adım 6: Yoklamayı Bitirme ve Tek Tıkla Excel / CSV Raporu Alma
* Sağ üstteki kırmızı **"Yoklamayı Bitir"** butonuna tıklayın.
* Oturum kapatılır ve anında **"Sonuçları İndir (CSV)"** butonu aktifleşir.
* Butona basın; inen CSV dosyasını açarak tüm öğrencilerin giriş saati, IP adresi ve yoklama yönteminin dökümünü hocaya gösterin.
* Raporlar sekmesine giderek dönemlik **%70 devamlılık analizi** tablosunu gösterin.

---

## ❓ 3. Hocanın Sorabileceği Sorular ve Hazır Cevaplarınız

| Hoca Ne Sorabilir? | Vereceğiniz Hazır Cevap |
| :--- | :--- |
| **"Sistem nerede barınıyor, benim bilgisayarıma bir şey kurmam gerekiyor mu?"** | Hayır hocam, sistem tamamen bulutta (Render.com) 7/24 kalıcı olarak yayındadır. İsteyen herkes interneti olan herhangi bir telefondan, tabletten veya bilgisayardan bağlanabilir. |
| **"Neden mobil uygulama (.apk) yapmadınız da web yaptınız?"** | Sınıfta herkese ayrı ayrı uygulama indirtmek (iOS/Android market uyumlulukları, depolama sorunları) dersin başında en az 20-30 dakika kaybettirir. Web-first mimari ile öğrenci hiçbir şey yüklemeden 3 saniyede yoklamasını verir. |
| **"Veritabanı olarak ne kullandınız?"** | SQLite3 ilişkisel veritabanı kullandık. 3. Normal Form'a (3NF) uygun 6 tablo ve Foreign Key kısıtları ile tasarlandı. |
| **"Öğretmen güvenliği nasıl sağlanıyor?"** | Öğretmen paneli Werkzeug SHA-256 parola özetleme (hashing) ve oturum (session) çerezleri ile yetkilendirilmiştir. Şifresiz kimse oturum başlatamaz veya raporları göremez. |
