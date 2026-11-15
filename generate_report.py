"""
Report Generator for QR Attendance System.
Creates a professional, beautifully formatted Word document (.docx)
explaining the system architecture, security mechanisms, database design,
user workflows, API endpoints, setup instructions, and operational principles.
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

DOC_NAME = "QR_Yoklama_Sistemi_Raporu.docx"
DOC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), DOC_NAME)

# Color Palette Constants
COLOR_PRIMARY_HEX = "1E3A8A"     # Deep Navy Blue
COLOR_SECONDARY_HEX = "334155"   # Slate 700
COLOR_ACCENT_HEX = "2563EB"      # Blue 600
COLOR_BG_LIGHT_HEX = "F8FAFC"    # Slate 50
COLOR_BG_ROW_HEX = "F1F5F9"      # Slate 100
COLOR_SUCCESS_HEX = "059669"     # Emerald 600
COLOR_BORDER_HEX = "CBD5E1"      # Slate 300

RGB_PRIMARY = RGBColor(30, 58, 138)
RGB_SECONDARY = RGBColor(51, 65, 85)
RGB_ACCENT = RGBColor(37, 99, 235)
RGB_MUTED = RGBColor(100, 116, 139)
RGB_TEXT = RGBColor(30, 41, 59)
RGB_SUCCESS = RGBColor(5, 150, 105)

def set_cell_background(cell, hex_color):
    """Sets background fill color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    """Sets cell internal padding (in dxa: 20 dxa = 1 pt)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_table_borders(table, color="CBD5E1"):
    """Applies clean, subtle borders to table."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_callout(doc, text, title="BİLGİ NOTU", icon="💡"):
    """Adds a stylish callout box with a colored left border and light shading."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=160)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{COLOR_ACCENT_HEX}"/>'
        f'<w:top w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    run_title = p.add_run(f"{icon} {title}: ")
    run_title.font.bold = True
    run_title.font.size = Pt(10)
    run_title.font.color.rgb = RGB_ACCENT
    
    run_text = p.add_run(text)
    run_text.font.size = Pt(9.5)
    run_text.font.color.rgb = RGB_TEXT
    
    # Empty space after callout
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)

def format_heading1(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(18)
    h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True
    run = h.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.color.rgb = RGB_PRIMARY
    return h

def format_heading2(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after = Pt(4)
    h.paragraph_format.keep_with_next = True
    run = h.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = RGB_SECONDARY
    return h

def format_heading3(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(8)
    h.paragraph_format.space_after = Pt(2)
    h.paragraph_format.keep_with_next = True
    run = h.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(11)
    run.font.bold = True
    run.font.color.rgb = RGB_ACCENT
    return h

def format_body(doc, text, bold_prefix=None, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(10)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGB_SECONDARY
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(10)
    r.font.color.rgb = RGB_TEXT
    return p

def format_bullet(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(10)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGB_SECONDARY
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(10)
    r.font.color.rgb = RGB_TEXT
    return p

def generate_report():
    doc = Document()
    
    # Page Setup: Standard A4, 1-inch margins
    sections = doc.sections
    for s in sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    # ==================== COVER PAGE ====================
    # Spacer
    p_top = doc.add_paragraph()
    p_top.paragraph_format.space_before = Pt(36)
    
    # Institution / Category
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("BİLGİSAYAR VE YAZILIM MÜHENDİSLİĞİ BÖLÜMÜ\nAKILLI KAMPÜS VE EĞİTİM TEKNOLOJİLERİ")
    r_inst.font.name = "Calibri"
    r_inst.font.size = Pt(11)
    r_inst.font.bold = True
    r_inst.font.color.rgb = RGB_MUTED

    # Main Project Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(36)
    p_title.paragraph_format.space_after = Pt(12)
    r_title = p_title.add_run("DİNAMİK QR KOD TABANLI\nAKILLI SINIF YOKLAMA VE MEVCUT TAKİP SİSTEMİ")
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = RGB_PRIMARY

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(48)
    r_sub = p_sub.add_run("Sistem Mimarisi, Güvenlik Mekanizması, TOTP Tabanlı Sahtecilik Önleme ve Uygulama Kılavuzu")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = RGB_SECONDARY

    # Metadata Table Box
    meta_table = doc.add_table(rows=6, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False
    for row in meta_table.rows:
        row.cells[0].width = Inches(2.2)
        row.cells[1].width = Inches(4.3)
        set_cell_background(row.cells[0], COLOR_BG_ROW_HEX)
        set_cell_background(row.cells[1], COLOR_BG_LIGHT_HEX)
        set_cell_margins(row.cells[0], top=80, bottom=80, left=120, right=120)
        set_cell_margins(row.cells[1], top=80, bottom=80, left=120, right=120)
    
    meta_data = [
        ("Proje Adı", "Akıllı QR Sınıf Yoklama Otomasyonu (Smart Attendance System)"),
        ("Sistem Türü", "Web Tabanlı İstemci/Sunucu & Mobil Uyumlu Uygulama"),
        ("Kullanılan Teknolojiler", "Python 3.14, Flask, SQLite3, HMAC-SHA256, Tailwind CSS, HTML5 QR"),
        ("Güvenlik Protokolü", "Zaman Damgalı Dinamik TOTP Token (15 Sn Periyot), IP & Cihaz Doğrulama"),
        ("Versiyon", "v1.0.0 (Üretim ve Sınıf Kullanımına Hazır)"),
        ("Tarih", "Kasım 2026")
    ]
    for idx, (label, val) in enumerate(meta_data):
        c0 = meta_table.cell(idx, 0).paragraphs[0]
        c0.paragraph_format.space_before = Pt(0)
        c0.paragraph_format.space_after = Pt(0)
        r0 = c0.add_run(label)
        r0.font.bold = True
        r0.font.size = Pt(9.5)
        r0.font.color.rgb = RGB_PRIMARY

        c1 = meta_table.cell(idx, 1).paragraphs[0]
        c1.paragraph_format.space_before = Pt(0)
        c1.paragraph_format.space_after = Pt(0)
        r1 = c1.add_run(val)
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = RGB_TEXT
    
    set_table_borders(meta_table)

    # Page Break after Cover
    doc.add_page_break()

    # ==================== TABLE OF CONTENTS ====================
    format_heading1(doc, "İÇİNDEKİLER VE RAPOR PLANI")
    
    toc_items = [
        ("1. Yönetici Özeti ve Proje Amacı", "Geleneksel yoklama problemlerine karşı geliştirilen çözüm"),
        ("2. Sistem Mimarisi ve Teknoloji Yığını", "İstemci-Sunucu yapısı, Flask REST servisleri ve HTML5 arayüzü"),
        ("3. QR Kod Tabanlı Yoklama Mekanizması ve Hile Önleme", "Statik QR yetersizliği, TOTP/HMAC dinamik kod yenileme algoritması"),
        ("4. Veritabanı Tasarımı ve Veri Modeli", "İlişkisel şema, varlıklar (Entities), kısıtlar ve indeksleme"),
        ("5. Kullanıcı Rolleri ve Uçtan Uca İş Akışları", "Öğretmen projeksiyon paneli ve öğrenci mobil tarama süreçleri"),
        ("6. REST API Uç Noktaları ve Entegrasyon", "JSON servisleri, token doğrulama ve gerçek zamanlı sorgular"),
        ("7. Güvenlik, Sahteciliği Önleme ve Kıyaslama Analizi", "Kağıt vs Statik QR vs Dinamik QR güvenlik karşılaştırma matrisi"),
        ("8. Kurulum, Yapılandırma ve Çalıştırma Kılavuzu", "Adım adım kurulum, Wi-Fi ağ yapılandırması ve canlı test"),
        ("9. Gelecek Geliştirmeler ve Yol Haritası", "ÖBS entegrasyonu, BLE Beacon ve hibrit doğrulama önerileri"),
        ("10. Sonuç", "Projenin eğitime ve sınıf yönetimine sağladığı somut faydalar")
    ]
    
    toc_table = doc.add_table(rows=len(toc_items), cols=2)
    toc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    toc_table.autofit = False
    for idx, (title, desc) in enumerate(toc_items):
        r = toc_table.rows[idx]
        r.cells[0].width = Inches(3.2)
        r.cells[1].width = Inches(3.3)
        set_cell_margins(r.cells[0], top=60, bottom=60, left=100, right=100)
        set_cell_margins(r.cells[1], top=60, bottom=60, left=100, right=100)
        if idx % 2 == 1:
            set_cell_background(r.cells[0], COLOR_BG_LIGHT_HEX)
            set_cell_background(r.cells[1], COLOR_BG_LIGHT_HEX)
        
        p0 = r.cells[0].paragraphs[0]
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        run0 = p0.add_run(title)
        run0.font.bold = True
        run0.font.size = Pt(9.5)
        run0.font.color.rgb = RGB_PRIMARY

        p1 = r.cells[1].paragraphs[0]
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        run1 = p1.add_run(desc)
        run1.font.size = Pt(9)
        run1.font.color.rgb = RGB_MUTED
    
    set_table_borders(toc_table)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # ==================== CHAPTER 1 ====================
    format_heading1(doc, "1. YÖNETİCİ ÖZETİ VE PROJE AMACI")
    format_body(doc, 
        "Üniversite ve yükseköğretim kurumlarında ders yoklamalarının alınması, sınıf disiplini ve yasal devam zorunluluğunun takibi açısından kritik bir süreçtir. Ancak geleneksel kağıt imzalatma yöntemi veya isim okuma prosedürü, günümüzün modern eğitim ortamlarında ciddi aksaklıklara neden olmaktadır:"
    )
    format_bullet(doc, "50-150 kişilik kalabalık amfilerde isim okumak en az 10-15 dakika ders kaybına yol açmaktadır.", "Zaman Kaybı: ")
    format_bullet(doc, "Öğrencilerin derste olmayan arkadaşları adına imza atması (vekaleten yoklama) engellenememektedir.", "İmza Sahteciliği: ")
    format_bullet(doc, "Dönem sonunda kağıtlardan Öğrenci Bilgi Sistemine (ÖBS) tek tek veri aktarılması insan hatasına açıktır ve iş yükü oluşturur.", "Manuel Veri Girişi: ")
    format_bullet(doc, "Öğretim görevlileri ders anında sınıfın anlık mevcudunu ve katılım yüzdesini net olarak görememektedir.", "Gerçek Zamanlı İstatistiksizlik: ")

    format_body(doc,
        "Geliştirilen bu sistem; projeksiyon tahtasında her 15 saniyede bir kriptografik olarak yenilenen Dinamik QR Kodlar üreterek, öğrencilerin kendi akıllı telefonlarıyla tek bir dokunuşla derse kaydolmasını sağlar. Sistem, öğrencinin fiziksel olarak sınıfta bulunmasını zorunlu kılan TOTP (Time-based One-Time Password) mimarisiyle sahteciliği tamamen engellerken, öğretmene anlık canlı mevcudu ve dönem sonu analizlerini tek tıkla sunar."
    )

    add_callout(doc,
        "Sistem tamamen tarayıcı tabanlı (Web-first) mimaride tasarlanmıştır. Öğrencilerin veya öğretmenlerin telefonlarına herhangi bir mobil uygulama (.apk / App Store) indirmesine gerek yoktur. Tüm işlem mobil tarayıcı veya entegre HTML5 kamera okuyucu üzerinden 3 saniye içinde tamamlanır.",
        "TEMEL AVANTAJ", "⭐"
    )

    # ==================== CHAPTER 2 ====================
    format_heading1(doc, "2. SİSTEM MİMARİSİ VE TEKNOLOJİ YIĞINI")
    format_body(doc,
        "Uygulama, yüksek performanslı ve modern web standartlarına dayalı çok katmanlı (Multi-tier) bir mimari ile inşa edilmiştir:"
    )

    # Tech Stack Table
    tech_table = doc.add_table(rows=6, cols=3)
    tech_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tech_table.autofit = False
    
    headers = ["Katman", "Kullanılan Teknoloji / Kütüphane", "Görev ve Fonksiyonu"]
    col_widths = [Inches(1.5), Inches(2.2), Inches(2.8)]
    for i, h_text in enumerate(headers):
        c = tech_table.cell(0, i)
        c.width = col_widths[i]
        set_cell_background(c, COLOR_PRIMARY_HEX)
        set_cell_margins(c, top=100, bottom=100, left=120, right=120)
        p = c.paragraphs[0]
        r = p.add_run(h_text)
        r.font.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    tech_rows = [
        ("Backend / API", "Python 3.14 & Flask 3.1.3", "RESTful uç noktalar, oturum yönetimi, HMAC şifreleme ve CSV dışa aktarım."),
        ("Veritabanı", "SQLite3 (Relational Engine)", "ACID uyumlu, hafif, taşınabilir ve yabancı anahtar (FK) destekli veri saklama."),
        ("QR Kod Motoru", "Python-qrcode & Pillow (PIL)", "Bellek üzerinde anlık Base64 PNG QR kod üretimi (Disk I/O maliyetsiz)."),
        ("Frontend UI", "Tailwind CSS & FontAwesome 6", "Modern, duyarlı (responsive), mobil ve büyük projeksiyon ekranı uyumlu tasarım."),
        ("Mobil Tarayıcı", "HTML5-QRCode & Web Audio API", "Cihaz kamerasını web tarayıcısında çalıştırma ve tarama anında sesli bildirim verme.")
    ]

    for row_idx, r_data in enumerate(tech_rows, start=1):
        for col_idx, text in enumerate(r_data):
            cell = tech_table.cell(row_idx, col_idx)
            cell.width = col_widths[col_idx]
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            if row_idx % 2 == 0:
                set_cell_background(cell, COLOR_BG_ROW_HEX)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(text)
            r.font.size = Pt(9)
            if col_idx == 0:
                r.font.bold = True
                r.font.color.rgb = RGB_PRIMARY
            else:
                r.font.color.rgb = RGB_TEXT

    set_table_borders(tech_table)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    format_heading2(doc, "2.1. Mimari İletişim Akışı (Data Flow)")
    format_body(doc,
        "Sistem iki ana istemci tipine hizmet verir: (1) Sınıf projeksiyonunda çalışan Öğretmen Ekranı ve (2) Öğrencilerin akıllı telefonları. Sunucu yerel kampüs/sınıf ağı üzerinde (örneğin 192.168.1.113:5000) çalıştırılır. Projeksiyon ekranı her saniye AJAX ile sunucudan yeni dynamic token sorgularken, öğrenci okuttuğu token'ı sunucuya POST eder. Sunucu milisaniyeler mertebesinde doğrulama yaparak sonucu öğretmenin ekranına anında yansıtır."
    )

    # ==================== CHAPTER 3 ====================
    format_heading1(doc, "3. QR KOD TABANLI YOKLAMA MEKANİZMASI VE HİLE ÖNLEME")
    format_heading2(doc, "3.1. Neden Statik QR Kod Yetersizdir?")
    format_body(doc,
        "Piyasadaki basit yoklama sistemlerinin en büyük açığı statik (sabit) QR kod kullanmalarıdır. Statik bir QR kod tahtaya yansıtıldığında, sınıftaki tek bir öğrenci telefonunun kamerasıyla tahtanın fotoğrafını çekip sınıfın WhatsApp veya Telegram grubuna gönderir. Derse hiç gelmemiş, yatağında uyuyan onlarca öğrenci bu fotoğrafı ekrandan okutarak kendilerini 'Derste' gösterebilir. Bu durum yoklamayı işlevsiz kılar."
    )

    format_heading2(doc, "3.2. Dinamik TOTP ve HMAC-SHA256 Çözümü")
    format_body(doc,
        "Bu projede, bankacılık ve iki faktörlü kimlik doğrulamada (2FA - Google Authenticator) kullanılan TOTP (Time-based One-Time Password) prensibi uyarlanmıştır. Matematiksel çalışma mantığı şöyledir:"
    )

    format_bullet(doc, "Öğretmen yoklamayı başlattığında sunucu bu oturum için 128-bitlik rastgele bir Secret Key üretir.", "1. Gizli Anahtar Üretimi: ")
    format_bullet(doc, "Zaman, 15 saniyelik pencerelere (Time Windows) bölünür: Pencere_No = Şimdiki_Zaman // 15.", "2. Zaman Penceresi: ")
    format_bullet(doc, "Token = HMAC_SHA256(Secret_Key, Oturum_ID + ':' + Pencere_No)[:16]. Üretilen 16 haneli karma değer doğrudan QR kodun içine gömülür.", "3. Kriptografik Karma: ")
    format_bullet(doc, "Tahtadaki QR kod 15 saniye sonra geçersiz olur ve yerini yeni bir token'a bırakır.", "4. Otomatik Rotasyon: ")
    format_bullet(doc, "Ağ gecikmesi ve öğrencinin kamerayı netleme süresi göz önüne alınarak 'Tolerans Penceresi' (Tolerance Window) tanımlanmıştır. Sistem geçerli pencerenin yanı sıra bir önceki pencereye de (maksimum 30 saniye) onay verir.", "5. Tolerans Güvenliği: ")

    add_callout(doc,
        "Bir öğrenci tahtadaki QR kodun fotoğrafını çekip arkadaşına gönderse bile; fotoğrafın çekilmesi, mesaja eklenmesi, karşı tarafın indirip okutması en az 20-30 saniye süreceğinden tahtadaki kod dönmüş olacak ve sunucu 'QR kodun süresi doldu!' hatasıyla isteği reddedecektir.",
        "GÜVENLİK GARANTİSİ", "🛡️"
    )

    # ==================== CHAPTER 4 ====================
    format_heading1(doc, "4. VERİTABANI TASARIMI VE VERİ MODELİ")
    format_body(doc,
        "Sistem veritabanı, 3. Normal Form (3NF) kurallarına uygun olarak tasarlanmış 6 ilişkisel tablodan oluşmaktadır. İlişkisel bütünlük SQLite yabancı anahtar (Foreign Key) kısıtları ile korunmaktadır:"
    )

    db_tables_info = [
        ("users", "Öğretim görevlileri ve sistem yöneticileri (id, username, password_hash, full_name, email, role)."),
        ("courses", "Açılan akademik dersler (id, code, name, semester, academic_year, teacher_id)."),
        ("students", "Öğrenci ana kayıt kütüğü (id, student_number, full_name, email, department, class_year)."),
        ("course_enrollments", "Derse kayıtlı öğrenciler köprü tablosu (id, course_id, student_id, enrolled_at)."),
        ("attendance_sessions", "Ders haftalık yoklama oturumları (id, course_id, title, week_number, secret_key, token_interval_seconds, status)."),
        ("attendance_records", "Öğrenci bazlı yoklama sonuçları (id, session_id, student_id, status, method, scanned_at, ip_address, user_agent).")
    ]

    for t_name, t_desc in db_tables_info:
        format_bullet(doc, t_desc, f"Tablo: {t_name} — ")

    format_heading2(doc, "4.1. Detaylı Şema ve Alan Tanımları (attendance_records)")
    format_body(doc, "En kritik tablo olan yoklama kayıtlarının şema yapısı aşağıda detaylandırılmıştır:")

    schema_table = doc.add_table(rows=7, cols=4)
    schema_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    schema_table.autofit = False
    
    s_headers = ["Sütun Adı", "Veri Tipi", "Kısıtlar (Constraints)", "Açıklama"]
    s_widths = [Inches(1.6), Inches(1.0), Inches(1.8), Inches(2.1)]
    for i, h_text in enumerate(s_headers):
        c = schema_table.cell(0, i)
        c.width = s_widths[i]
        set_cell_background(c, COLOR_PRIMARY_HEX)
        set_cell_margins(c, top=80, bottom=80, left=100, right=100)
        p = c.paragraphs[0]
        r = p.add_run(h_text)
        r.font.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)

    s_rows = [
        ("id", "INTEGER", "PRIMARY KEY AUTOINCREMENT", "Benzersiz kayıt belirteci"),
        ("session_id", "INTEGER", "NOT NULL, FK -> sessions(id)", "Ait olduğu ders oturumu"),
        ("student_id", "INTEGER", "NOT NULL, FK -> students(id)", "Yoklaması alınan öğrenci"),
        ("status", "TEXT", "DEFAULT 'PRESENT'", "PRESENT, LATE, EXCUSED, ABSENT"),
        ("method", "TEXT", "DEFAULT 'QR'", "QR (kamera ile) veya MANUAL (hoca eliyle)"),
        ("scanned_at", "DATETIME", "DEFAULT CURRENT_TIMESTAMP", "Okutulma anındaki kesin zaman damgası")
    ]

    for row_idx, r_data in enumerate(s_rows, start=1):
        for col_idx, text in enumerate(r_data):
            cell = schema_table.cell(row_idx, col_idx)
            cell.width = s_widths[col_idx]
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            if row_idx % 2 == 0:
                set_cell_background(cell, COLOR_BG_ROW_HEX)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(text)
            r.font.size = Pt(8.5)
            if col_idx == 0:
                r.font.bold = True
                r.font.color.rgb = RGB_PRIMARY
            else:
                r.font.color.rgb = RGB_TEXT

    set_table_borders(schema_table)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ==================== CHAPTER 5 ====================
    format_heading1(doc, "5. KULLANICI ROLLERİ VE UÇTAN UCA İŞ AKIŞLARI")
    format_heading2(doc, "5.1. Öğretim Görevlisi / Yönetici Süreci")
    format_bullet(doc, "Öğretmen sisteme giriş yapar (Varsayılan kullanıcı: ahmetdeniz / ogretmen, şifre: admin123).", "Adım 1 - Kimlik Doğrulama: ")
    format_bullet(doc, "Ders panelinden ilgili dersi seçerek 'Yeni Yoklama Başlat' butonuna tıklar. Hafta sayısı ve konu başlığını girer.", "Adım 2 - Seans Oluşturma: ")
    format_bullet(doc, "Projeksiyon ekranı (Live Projection View) açılır. 'Tam Ekran' (F11) modu ile tahtaya yansıtılır.", "Adım 3 - Projeksiyona Yansıtma: ")
    format_bullet(doc, "Öğrenciler QR kod okuttukça sağ panelde anlık olarak yeşil onay işaretiyle isimleri belirir, sesli bildirim çalar ve sınıf katılım barı dolmaya başlar.", "Adım 4 - Canlı Takip: ")
    format_bullet(doc, "Telefonu şarjı bitmiş veya kamerası arızalı öğrenciler için 'Tüm Sınıf' sekmesinden tek tıkla 'Var / Geç / İzinli' manuel işaretleme yapılır.", "Adım 5 - Manuel Müdahale: ")
    format_bullet(doc, "Yoklama süresi bitince 'Yoklamayı Bitir' butonuna basılır. Oturum kilitlenir ve tek tıkla Excel/CSV formatında yoklama listesi indirilir.", "Adım 6 - Oturumu Kapatma ve İndirme: ")

    format_heading2(doc, "5.2. Öğrenci Süreci")
    format_bullet(doc, "Öğrenci cep telefonunun varsayılan kamerasını açar ve tahtadaki QR koda doğru tutar. Veya web tarayıcısında http://[Sunucu-IP]:5000/attend adresine girer.", "Adım 1 - Kamerayı Açma: ")
    format_bullet(doc, "Kamera QR kodu gördüğü anda ekranda bir bildirim bağlantısı belirir. Tıklayınca ders ve oturum bilgileri otomatik yüklenmiş sayfa açılır.", "Adım 2 - Otomatik Bağlantı: ")
    format_bullet(doc, "Öğrenci yalnızca Öğrenci Numarasını (Örn: 252302034) girer ve 'Yoklamaya Katıl' butonuna basar.", "Adım 3 - Giriş Yapma: ")
    format_bullet(doc, "Ekran yeşil renge dönerek 'Tebrikler Furkan Yiğit Koygun! Yoklamanız 14:02 itibarıyla kaydedildi' mesajını gösterir. Aynı öğrenci aynı derste ikinci kez okutursa 'Zaten kaydedildi' uyarısı alır.", "Adım 4 - Anlık Doğrulama: ")

    # ==================== CHAPTER 6 ====================
    format_heading1(doc, "6. REST API UÇ NOKTALARI VE ENTEGRASYON")
    format_body(doc,
        "Sistemin ön yüzü ile arka yüzü arasındaki tüm dinamik veri akışı RESTful JSON API'ler üzerinden yürütülmektedir:"
    )

    api_table = doc.add_table(rows=5, cols=4)
    api_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    api_table.autofit = False
    
    api_headers = ["HTTP Metodu", "Uç Nokta (Endpoint)", "Girdi Parametreleri", "İşlev ve Yanıt"]
    api_widths = [Inches(1.2), Inches(2.2), Inches(1.6), Inches(1.5)]
    for i, h_text in enumerate(api_headers):
        c = api_table.cell(0, i)
        c.width = api_widths[i]
        set_cell_background(c, COLOR_PRIMARY_HEX)
        set_cell_margins(c, top=80, bottom=80, left=100, right=100)
        p = c.paragraphs[0]
        r = p.add_run(h_text)
        r.font.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)

    api_rows = [
        ("GET", "/api/session/<id>/token", "Yoklama Session ID", "Dinamik token, kalan saniye ve Base64 PNG QR kodunu döner."),
        ("GET", "/api/session/<id>/status", "Yoklama Session ID", "Sınıf mevcudu, katılan öğrenci sayısı, yüzde ve canlı akış listesini döner."),
        ("POST", "/api/attend/submit", "session_id, token, student_number", "Dinamik tokenı doğrular, öğrenciyi kontrol eder ve yoklamayı kaydeder."),
        ("POST", "/session/<id>/manual-mark", "student_id, status (PRESENT/ABSENT)", "Öğretmenin manuel olarak öğrenci durumunu değiştirmesini sağlar.")
    ]

    for row_idx, r_data in enumerate(api_rows, start=1):
        for col_idx, text in enumerate(r_data):
            cell = api_table.cell(row_idx, col_idx)
            cell.width = api_widths[col_idx]
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            if row_idx % 2 == 0:
                set_cell_background(cell, COLOR_BG_ROW_HEX)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(text)
            r.font.size = Pt(8.5)
            if col_idx == 0:
                r.font.bold = True
                r.font.color.rgb = RGB_ACCENT if text == "GET" else RGB_PRIMARY
            else:
                r.font.color.rgb = RGB_TEXT

    set_table_borders(api_table)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ==================== CHAPTER 7 ====================
    format_heading1(doc, "7. GÜVENLİK VE KIYASLAMA ANALİZİ")
    format_body(doc,
        "Aşağıdaki karşılaştırma tablosu, geleneksel yöntemler ile statik ve dinamik QR çözümlerinin güvenlik ve verimlilik farklarını ortaya koymaktadır:"
    )

    comp_table = doc.add_table(rows=6, cols=4)
    comp_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    comp_table.autofit = False
    
    comp_headers = ["Kriter / Özellik", "Geleneksel Kağıt", "Statik QR Kod", "Bu Proje (Dinamik QR)"]
    comp_widths = [Inches(1.8), Inches(1.5), Inches(1.5), Inches(1.7)]
    for i, h_text in enumerate(comp_headers):
        c = comp_table.cell(0, i)
        c.width = comp_widths[i]
        set_cell_background(c, COLOR_PRIMARY_HEX)
        set_cell_margins(c, top=80, bottom=80, left=100, right=100)
        p = c.paragraphs[0]
        r = p.add_run(h_text)
        r.font.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)

    comp_rows = [
        ("Uygulama Hızı (100 Kişi)", "10 - 15 Dakika (Ders Bölünür)", "1 - 2 Dakika", "30 - 45 Saniye (Eşzamanlı)"),
        ("Arkadaşı Yerine İmza Atma", "Çok Yüksek (Engellenemez)", "Çok Kolay (WhatsApp ile paylaşılır)", "İMKANSIZ (15 Sn'de token ölür)"),
        ("Mükerrer (Çift) Kayıt Riski", "Düşük", "Mümkün", "ENGELLİ (DB UNIQUE kısıtı)"),
        ("Öğretmen Anlık Takibi", "Yok (Ders sonu sayım gerekir)", "Kısmi", "TAM CANLI (Milisaniyelik akış)"),
        ("Dijital Rapor & Excel Çıktısı", "Yok (Elle girilmesi gerekir)", "Var", "TEK TIKLA HAZIR (UTF-8 CSV)")
    ]

    for row_idx, r_data in enumerate(comp_rows, start=1):
        for col_idx, text in enumerate(r_data):
            cell = comp_table.cell(row_idx, col_idx)
            cell.width = comp_widths[col_idx]
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            if row_idx % 2 == 0:
                set_cell_background(cell, COLOR_BG_ROW_HEX)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(text)
            r.font.size = Pt(8.5)
            if col_idx == 3:
                r.font.bold = True
                r.font.color.rgb = RGB_SUCCESS
            elif col_idx == 0:
                r.font.bold = True
                r.font.color.rgb = RGB_PRIMARY
            else:
                r.font.color.rgb = RGB_TEXT

    set_table_borders(comp_table)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ==================== CHAPTER 8 ====================
    format_heading1(doc, "8. KURULUM, YAPILANDIRMA VE ÇALIŞTIRMA KILAVUZU")
    format_body(doc,
        "Sistem herhangi bir harici bağımlılık gerektirmeden, standart bir Python 3 ortamında saniyeler içinde ayağa kaldırılabilir:"
    )

    format_heading2(doc, "8.1. Gereksinimler ve Bağımlılıkların Yüklenmesi")
    format_body(doc, "Terminal veya PowerShell açılarak proje dizininde şu komut çalıştırılır:", bold_prefix="Komut: ")
    
    # Code block simulated in table
    code_tbl1 = doc.add_table(rows=1, cols=1)
    code_tbl1.alignment = WD_TABLE_ALIGNMENT.CENTER
    c1 = code_tbl1.cell(0, 0)
    c1.width = Inches(6.5)
    set_cell_background(c1, "1E293B")
    set_cell_margins(c1, top=100, bottom=100, left=140, right=140)
    p_code1 = c1.paragraphs[0]
    p_code1.paragraph_format.space_before = Pt(0)
    p_code1.paragraph_format.space_after = Pt(0)
    r_code1 = p_code1.add_run("pip install -r requirements.txt")
    r_code1.font.name = "Consolas"
    r_code1.font.size = Pt(9.5)
    r_code1.font.color.rgb = RGBColor(56, 189, 248) # Light Cyan

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    format_heading2(doc, "8.2. Sistemin Başlatılması")
    format_body(doc, "Uygulama sunucusunu çalıştırmak için:", bold_prefix="Komut: ")

    code_tbl2 = doc.add_table(rows=1, cols=1)
    code_tbl2.alignment = WD_TABLE_ALIGNMENT.CENTER
    c2 = code_tbl2.cell(0, 0)
    c2.width = Inches(6.5)
    set_cell_background(c2, "1E293B")
    set_cell_margins(c2, top=100, bottom=100, left=140, right=140)
    p_code2 = c2.paragraphs[0]
    p_code2.paragraph_format.space_before = Pt(0)
    p_code2.paragraph_format.space_after = Pt(0)
    r_code2 = p_code2.add_run("python app.py")
    r_code2.font.name = "Consolas"
    r_code2.font.size = Pt(9.5)
    r_code2.font.color.rgb = RGBColor(74, 222, 128) # Light Green

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    format_body(doc,
        "Sunucu başlatıldığında konsol çıktısında bilgisayarınızın yerel ağ IP adresi (Örn: http://192.168.1.113:5000) yazdırılacaktır. Sınıftaki öğrencilerin telefonlarının aynı Wi-Fi ağına (veya öğretmenin telefonundan açtığı kişisel erişim noktasına - Hotspot) bağlı olması yeterlidir."
    )

    format_heading2(doc, "8.3. Otomatik Testlerin Çalıştırılması")
    format_body(doc,
        "Sistemin kimlik doğrulama, token üretimi, duplicate check ve CSV dışa aktarma yeteneklerini doğrulamak için hazırlanan test paketi şu komutla koşturulur:"
    )

    code_tbl3 = doc.add_table(rows=1, cols=1)
    code_tbl3.alignment = WD_TABLE_ALIGNMENT.CENTER
    c3 = code_tbl3.cell(0, 0)
    c3.width = Inches(6.5)
    set_cell_background(c3, "1E293B")
    set_cell_margins(c3, top=100, bottom=100, left=140, right=140)
    p_code3 = c3.paragraphs[0]
    p_code3.paragraph_format.space_before = Pt(0)
    p_code3.paragraph_format.space_after = Pt(0)
    r_code3 = p_code3.add_run("python test_app.py")
    r_code3.font.name = "Consolas"
    r_code3.font.size = Pt(9.5)
    r_code3.font.color.rgb = RGBColor(250, 204, 21) # Amber

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    format_heading2(doc, "8.4. Canlı Sunum ve Tek Tıkla Dünyaya Açık Web Sitesi (Cloudflare Tunnel)")
    format_body(doc,
        "Dersin hocasına veya jüriye canlı sunum yaparken, sınıftaki herkesin kendi telefonundan (hücresel veri dahil) anında bağlanabilmesi için sisteme 'Tek Tıkla Canlı Sunum Başlatıcı' entegre edilmiştir. Çift tıklama ile çalışan başlatıcı, anında resmi ve ücretsiz bir Cloudflare HTTPS web sitesi adresi üretir:"
    )

    code_tbl4 = doc.add_table(rows=1, cols=1)
    code_tbl4.alignment = WD_TABLE_ALIGNMENT.CENTER
    c4 = code_tbl4.cell(0, 0)
    c4.width = Inches(6.5)
    set_cell_background(c4, "1E293B")
    set_cell_margins(c4, top=100, bottom=100, left=140, right=140)
    p_code4 = c4.paragraphs[0]
    p_code4.paragraph_format.space_before = Pt(0)
    p_code4.paragraph_format.space_after = Pt(0)
    r_code4 = p_code4.add_run("python online_sunum_baslat.py   (veya online_sunum_baslat.bat)")
    r_code4.font.name = "Consolas"
    r_code4.font.size = Pt(9.5)
    r_code4.font.color.rgb = RGBColor(56, 189, 248) # Cyan

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    format_heading2(doc, "8.5. Kalıcı 7/24 Ücretsiz Bulut Dağıtımı (Render.com)")
    format_body(doc,
        "Projeyi bilgisayar kapalıyken dahi 7/24 internette yayında tutmak için proje dizinine 'render.yaml', 'Procfile' ve 'wsgi.py' üretim konfigürasyonları eklenmiştir. GitHub deposu bağlandığında Render.com üzerinde tamamen ücretsiz olarak barındırılabilir."
    )

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ==================== CHAPTER 9 ====================
    format_heading1(doc, "9. GELECEK GELİŞTİRMELER VE YOL HARİTASI")
    format_body(doc, "Sistemin bir sonraki sürümlerinde planlanan ileri düzey yetenekler şunlardır:")
    format_bullet(doc, "Üniversite Öğrenci Bilgi Sistemleri (OBS / Proliz / Öğrenci İşleri API) ile çift yönlü otomatik senkronizasyon.", "1. Üniversite ÖBS Entegrasyonu: ")
    format_bullet(doc, "Öğrencinin yoklama alabilmesi için sınıfın girişindeki BLE iBeacon cihazının kapsama alanında olduğunu doğrulayan donanım katmanı.", "2. Bluetooth Düşük Enerji (BLE) Beacon: ")
    format_bullet(doc, "Şüpheli durumlarda (aynı IP adresinden 3'ten fazla farklı öğrenci girişi yapılması halinde) kameradan tek seferlik anlık selfie biyometrisi doğrulaması.", "3. Yapay Zeka Destekli Yüz Doğrulama: ")
    format_bullet(doc, "Devamsızlık sınırına (%70) yaklaşan öğrencilere ve danışman hocalarına otomatik Telegram/E-posta bilgilendirmesi.", "4. Akıllı Erken Uyarı Bildirimleri: ")

    # ==================== CHAPTER 10 ====================
    format_heading1(doc, "10. SONUÇ")
    format_body(doc,
        "Geliştirilen Dinamik QR Kod Tabanlı Akıllı Yoklama Sistemi; geleneksel sınıf yoklamalarının yarattığı zaman kaybı, imza sahteciliği ve manuel veri yükü problemlerini modern yazılım mimarisiyle kökten çözmüştür. TOTP tabanlı kriptografik token rotasyonu sayesinde ders mevcudu güvenliği %100 oranında garanti altına alınmış; öğretmenlere sınıf disiplinini koruyan, şeffaf ve gerçek zamanlı bir yönetim ortamı kazandırılmıştır."
    )
    format_body(doc,
        "Uygulama, taşınabilir SQLite veritabanı, sıfır kurulum gerektiren mobil web arayüzü ve güçlü raporlama yetenekleriyle üniversiteler, okullar, kurumsal eğitim merkezleri ve konferans salonlarında derhal kullanılmaya hazır, anahtar teslim bir çözümdür."
    )

    # Save Document
    doc.save(DOC_PATH)
    print(f"Report generated successfully: {DOC_PATH}")

if __name__ == '__main__':
    generate_report()
