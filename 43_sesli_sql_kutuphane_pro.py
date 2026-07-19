import sqlite3
import subprocess
import getpass
import tempfile
import os

from datetime import datetime, timedelta

import sounddevice as sd
import speech_recognition as sr
from scipy.io.wavfile import write


# --------------------------------------------------
# SABİTLER
# --------------------------------------------------

VERITABANI_ADI = "kutuphane_43.db"
YONETICI_SIFRESI = "2580"
ODUNC_SURESI_GUN = 14

SES_KAYIT_SURESI = 5
ORNEKLEME_HIZI = 44100


# --------------------------------------------------
# YARDIMCI FONKSİYONLAR
# --------------------------------------------------

def tarih_saat_al():
    return datetime.now().strftime(
        "%d.%m.%Y %H:%M:%S"
    )


def bugunun_tarihi():
    return datetime.now().strftime(
        "%Y-%m-%d"
    )


def tarih_goster(tarih_metni):

    if not tarih_metni:
        return "-"

    try:

        tarih = datetime.strptime(
            tarih_metni,
            "%Y-%m-%d"
        )

        return tarih.strftime(
            "%d.%m.%Y"
        )

    except ValueError:
        return tarih_metni


def seslendir(metin):

    try:

        subprocess.run(
            ["say", str(metin)],
            check=False
        )

    except (FileNotFoundError, OSError):
        pass


def mesaj_yaz(metin, sesli=True):

    print(metin)

    if sesli:
        seslendir(metin)


def guvenli_sifre_al(mesaj):

    try:
        return getpass.getpass(
            mesaj
        ).strip()

    except (EOFError, OSError):
        return input(
            mesaj
        ).strip()


def yonetici_sifresi_dogrula():

    sifre = guvenli_sifre_al(
        "\nYönetici şifresini giriniz: "
    )

    if sifre == YONETICI_SIFRESI:

        mesaj_yaz(
            "\nŞifre doğru. Yetki verildi."
        )

        return True

    mesaj_yaz(
        "\nŞifre yanlış. İşlem iptal edildi."
    )

    return False


# --------------------------------------------------
# SESLİ KOMUT
# --------------------------------------------------

def sesli_komut_al():

    gecici_dosya = None

    try:

        print("\n🎙️ Konuşmaya başlayın.")
        print(
            f"{SES_KAYIT_SURESI} saniye "
            "boyunca dinleniyor..."
        )

        ses = sd.rec(
            int(
                SES_KAYIT_SURESI
                * ORNEKLEME_HIZI
            ),
            samplerate=ORNEKLEME_HIZI,
            channels=1,
            dtype="int16"
        )

        sd.wait()

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as dosya:

            gecici_dosya = dosya.name

        write(
            gecici_dosya,
            ORNEKLEME_HIZI,
            ses
        )

        taniyici = sr.Recognizer()

        with sr.AudioFile(
            gecici_dosya
        ) as kaynak:

            ses_verisi = taniyici.record(
                kaynak
            )

        komut = taniyici.recognize_google(
            ses_verisi,
            language="tr-TR"
        )

        print(
            f"\nAlgılanan komut: {komut}"
        )

        return komut.lower().strip()

    except sr.UnknownValueError:

        print(
            "\nSöylediğiniz anlaşılamadı."
        )

        return None

    except sr.RequestError as hata:

        print(
            "\nSes tanıma servisine "
            "ulaşılamadı:"
        )

        print(hata)

        return None

    except (
        sd.PortAudioError,
        OSError,
        ValueError
    ) as hata:

        print(
            "\nMikrofon hatası oluştu:"
        )

        print(hata)

        return None

    finally:

        if (
            gecici_dosya
            and os.path.exists(gecici_dosya)
        ):

            try:
                os.remove(gecici_dosya)

            except OSError:
                pass


def menu_secimi_al():

    tercih = input(
        "\nMenü numarası giriniz\n"
        "veya sesli komut için V yazınız: "
    ).strip().lower()

    if tercih != "v":
        return tercih

    komut = sesli_komut_al()

    if komut is None:

        mesaj_yaz(
            "\nSesli komut alınamadı. "
            "Klavye ile devam ediliyor."
        )

        return input(
            "Menü numarası: "
        ).strip()

    komutlar = {
        "kitapları göster": "1",
        "kitapları listele": "1",
        "tüm kitaplar": "1",

        "kitap ara": "2",
        "arama yap": "2",

        "kitap ekle": "3",
        "yeni kitap ekle": "3",

        "kitap sil": "4",

        "üyeleri göster": "5",
        "üyeleri listele": "5",

        "üye ekle": "6",
        "yeni üye ekle": "6",

        "üye sil": "7",

        "ödünç ver": "8",
        "kitap ödünç ver": "8",

        "iade al": "9",
        "kitap iade": "9",

        "geciken kitaplar": "10",

        "üye kitapları": "11",
        "üyenin kitapları": "11",

        "işlem geçmişi": "12",

        "çıkış": "0",
        "programı kapat": "0"
    }

    if komut in komutlar:
        return komutlar[komut]

    for metin, numara in komutlar.items():

        if metin in komut:
            return numara

    mesaj_yaz(
        "\nKomut anlaşılamadı. "
        "Klavye ile devam ediliyor."
    )

    return input(
        "Menü numarası: "
    ).strip()


# --------------------------------------------------
# VERİTABANI SINIFI
# --------------------------------------------------

class KutuphaneVeritabani:

    def __init__(self):

        self.baglanti = sqlite3.connect(
            VERITABANI_ADI
        )

        self.baglanti.row_factory = (
            sqlite3.Row
        )

        self.imlec = (
            self.baglanti.cursor()
        )

        self.imlec.execute(
            "PRAGMA foreign_keys = ON"
        )

        self.tablolari_olustur()
        self.ornek_verileri_olustur()

    def tablolari_olustur(self):

        self.imlec.execute("""
            CREATE TABLE IF NOT EXISTS kitaplar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kitap_adi TEXT NOT NULL,
                yazar TEXT NOT NULL,
                kategori TEXT NOT NULL,
                isbn TEXT UNIQUE NOT NULL,
                yayin_yili INTEGER,
                durum TEXT NOT NULL DEFAULT 'MUSAIT',
                eklenme_tarihi TEXT NOT NULL
            )
        """)

        self.imlec.execute("""
            CREATE TABLE IF NOT EXISTS uyeler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad_soyad TEXT NOT NULL,
                telefon TEXT,
                eposta TEXT UNIQUE,
                kayit_tarihi TEXT NOT NULL,
                aktif INTEGER NOT NULL DEFAULT 1
            )
        """)

        self.imlec.execute("""
            CREATE TABLE IF NOT EXISTS oduncler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kitap_id INTEGER NOT NULL,
                uye_id INTEGER NOT NULL,
                odunc_tarihi TEXT NOT NULL,
                son_teslim_tarihi TEXT NOT NULL,
                iade_tarihi TEXT,
                durum TEXT NOT NULL DEFAULT 'ODUNC',

                FOREIGN KEY (kitap_id)
                REFERENCES kitaplar(id),

                FOREIGN KEY (uye_id)
                REFERENCES uyeler(id)
            )
        """)

        self.imlec.execute("""
            CREATE TABLE IF NOT EXISTS islemler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                islem_turu TEXT NOT NULL,
                aciklama TEXT NOT NULL,
                tarih TEXT NOT NULL
            )
        """)

        self.baglanti.commit()

    def ornek_verileri_olustur(self):

        self.imlec.execute("""
            SELECT COUNT(*) AS sayi
            FROM kitaplar
        """)

        kitap_sayisi = (
            self.imlec.fetchone()["sayi"]
        )

        if kitap_sayisi == 0:

            kitaplar = [
                (
                    "Python ile Programlama",
                    "Ahmet Yılmaz",
                    "Yazılım",
                    "9780000000001",
                    2025,
                    "MUSAIT",
                    tarih_saat_al()
                ),
                (
                    "Veritabanı Sistemleri",
                    "Mehmet Kaya",
                    "Bilgisayar",
                    "9780000000002",
                    2024,
                    "MUSAIT",
                    tarih_saat_al()
                ),
                (
                    "Siber Güvenliğe Giriş",
                    "Selin Demir",
                    "Siber Güvenlik",
                    "9780000000003",
                    2026,
                    "MUSAIT",
                    tarih_saat_al()
                )
            ]

            self.imlec.executemany("""
                INSERT INTO kitaplar (
                    kitap_adi,
                    yazar,
                    kategori,
                    isbn,
                    yayin_yili,
                    durum,
                    eklenme_tarihi
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, kitaplar)

        self.imlec.execute("""
            SELECT COUNT(*) AS sayi
            FROM uyeler
        """)

        uye_sayisi = (
            self.imlec.fetchone()["sayi"]
        )

        if uye_sayisi == 0:

            self.imlec.execute("""
                INSERT INTO uyeler (
                    ad_soyad,
                    telefon,
                    eposta,
                    kayit_tarihi,
                    aktif
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                "Ayaz Kullanıcı",
                "05000000000",
                "ayaz@example.com",
                tarih_saat_al(),
                1
            ))

        self.baglanti.commit()

    def islem_kaydet(
        self,
        islem_turu,
        aciklama
    ):

        self.imlec.execute("""
            INSERT INTO islemler (
                islem_turu,
                aciklama,
                tarih
            )
            VALUES (?, ?, ?)
        """, (
            islem_turu,
            aciklama,
            tarih_saat_al()
        ))

    def kitaplari_getir(self):

        self.imlec.execute("""
            SELECT *
            FROM kitaplar
            ORDER BY kitap_adi
        """)

        return self.imlec.fetchall()

    def kitap_ara(self, arama):

        arama = f"%{arama}%"

        self.imlec.execute("""
            SELECT *
            FROM kitaplar
            WHERE kitap_adi LIKE ?
               OR yazar LIKE ?
               OR kategori LIKE ?
               OR isbn LIKE ?
            ORDER BY kitap_adi
        """, (
            arama,
            arama,
            arama,
            arama
        ))

        return self.imlec.fetchall()

    def kitap_bul(self, kitap_id):

        self.imlec.execute("""
            SELECT *
            FROM kitaplar
            WHERE id = ?
        """, (kitap_id,))

        return self.imlec.fetchone()

    def kitap_ekle(
        self,
        kitap_adi,
        yazar,
        kategori,
        isbn,
        yayin_yili
    ):

        try:

            self.imlec.execute("""
                INSERT INTO kitaplar (
                    kitap_adi,
                    yazar,
                    kategori,
                    isbn,
                    yayin_yili,
                    durum,
                    eklenme_tarihi
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                kitap_adi,
                yazar,
                kategori,
                isbn,
                yayin_yili,
                "MUSAIT",
                tarih_saat_al()
            ))

            kitap_id = (
                self.imlec.lastrowid
            )

            self.islem_kaydet(
                "KİTAP EKLEME",
                (
                    f"{kitap_adi} adlı "
                    "kitap eklendi."
                )
            )

            self.baglanti.commit()

            return True, kitap_id

        except sqlite3.IntegrityError:

            self.baglanti.rollback()

            return False, None

    def kitap_sil(self, kitap_id):

        kitap = self.kitap_bul(
            kitap_id
        )

        if kitap is None:
            return False, "Kitap bulunamadı."

        if kitap["durum"] == "ODUNC":

            return (
                False,
                "Ödünçteki kitap silinemez."
            )

        self.imlec.execute("""
            DELETE FROM kitaplar
            WHERE id = ?
        """, (kitap_id,))

        self.islem_kaydet(
            "KİTAP SİLME",
            (
                f"{kitap['kitap_adi']} adlı "
                "kitap silindi."
            )
        )

        self.baglanti.commit()

        return True, "Kitap silindi."

    def uyeleri_getir(self):

        self.imlec.execute("""
            SELECT *
            FROM uyeler
            WHERE aktif = 1
            ORDER BY ad_soyad
        """)

        return self.imlec.fetchall()

    def uye_bul(self, uye_id):

        self.imlec.execute("""
            SELECT *
            FROM uyeler
            WHERE id = ?
        """, (uye_id,))

        return self.imlec.fetchone()

    def uye_ekle(
        self,
        ad_soyad,
        telefon,
        eposta
    ):

        try:

            self.imlec.execute("""
                INSERT INTO uyeler (
                    ad_soyad,
                    telefon,
                    eposta,
                    kayit_tarihi,
                    aktif
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                ad_soyad,
                telefon,
                eposta,
                tarih_saat_al(),
                1
            ))

            uye_id = (
                self.imlec.lastrowid
            )

            self.islem_kaydet(
                "ÜYE EKLEME",
                (
                    f"{ad_soyad} adlı "
                    "üye eklendi."
                )
            )

            self.baglanti.commit()

            return True, uye_id

        except sqlite3.IntegrityError:

            self.baglanti.rollback()

            return False, None

    def uye_sil(self, uye_id):

        uye = self.uye_bul(
            uye_id
        )

        if uye is None:
            return False, "Üye bulunamadı."

        self.imlec.execute("""
            SELECT COUNT(*) AS sayi
            FROM oduncler
            WHERE uye_id = ?
              AND durum = 'ODUNC'
        """, (uye_id,))

        aktif_odunc = (
            self.imlec.fetchone()["sayi"]
        )

        if aktif_odunc > 0:

            return (
                False,
                "Üyenin iade etmediği "
                "kitaplar bulunuyor."
            )

        self.imlec.execute("""
            UPDATE uyeler
            SET aktif = 0
            WHERE id = ?
        """, (uye_id,))

        self.islem_kaydet(
            "ÜYE SİLME",
            (
                f"{uye['ad_soyad']} adlı "
                "üye pasif yapıldı."
            )
        )

        self.baglanti.commit()

        return (
            True,
            "Üye kaydı pasif yapıldı."
        )

    def kitap_odunc_ver(
        self,
        kitap_id,
        uye_id
    ):

        kitap = self.kitap_bul(
            kitap_id
        )

        uye = self.uye_bul(
            uye_id
        )

        if kitap is None:
            return False, "Kitap bulunamadı."

        if (
            uye is None
            or uye["aktif"] != 1
        ):

            return (
                False,
                "Aktif üye bulunamadı."
            )

        if kitap["durum"] != "MUSAIT":

            return (
                False,
                "Kitap şu anda müsait değil."
            )

        odunc_tarihi = datetime.now()

        son_teslim = (
            odunc_tarihi
            + timedelta(
                days=ODUNC_SURESI_GUN
            )
        )

        try:

            self.imlec.execute("""
                INSERT INTO oduncler (
                    kitap_id,
                    uye_id,
                    odunc_tarihi,
                    son_teslim_tarihi,
                    iade_tarihi,
                    durum
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                kitap_id,
                uye_id,
                odunc_tarihi.strftime(
                    "%Y-%m-%d"
                ),
                son_teslim.strftime(
                    "%Y-%m-%d"
                ),
                None,
                "ODUNC"
            ))

            self.imlec.execute("""
                UPDATE kitaplar
                SET durum = 'ODUNC'
                WHERE id = ?
            """, (kitap_id,))

            self.islem_kaydet(
                "ÖDÜNÇ VERME",
                (
                    f"{kitap['kitap_adi']} "
                    f"kitabı {uye['ad_soyad']} "
                    "adlı üyeye verildi."
                )
            )

            self.baglanti.commit()

            return (
                True,
                son_teslim.strftime(
                    "%Y-%m-%d"
                )
            )

        except sqlite3.Error:

            self.baglanti.rollback()
            raise

    def kitap_iade_al(self, kitap_id):

        kitap = self.kitap_bul(
            kitap_id
        )

        if kitap is None:
            return False, "Kitap bulunamadı."

        self.imlec.execute("""
            SELECT
                oduncler.*,
                uyeler.ad_soyad
            FROM oduncler

            JOIN uyeler
                ON uyeler.id = oduncler.uye_id

            WHERE oduncler.kitap_id = ?
              AND oduncler.durum = 'ODUNC'

            ORDER BY oduncler.id DESC
            LIMIT 1
        """, (kitap_id,))

        odunc = self.imlec.fetchone()

        if odunc is None:

            return (
                False,
                "Bu kitap ödünçte görünmüyor."
            )

        try:

            self.imlec.execute("""
                UPDATE oduncler
                SET
                    iade_tarihi = ?,
                    durum = 'IADE'
                WHERE id = ?
            """, (
                bugunun_tarihi(),
                odunc["id"]
            ))

            self.imlec.execute("""
                UPDATE kitaplar
                SET durum = 'MUSAIT'
                WHERE id = ?
            """, (kitap_id,))

            self.islem_kaydet(
                "KİTAP İADE",
                (
                    f"{kitap['kitap_adi']} "
                    f"kitabı {odunc['ad_soyad']} "
                    "adlı üyeden alındı."
                )
            )

            self.baglanti.commit()

            son_teslim = datetime.strptime(
                odunc["son_teslim_tarihi"],
                "%Y-%m-%d"
            ).date()

            bugun = datetime.now().date()

            gecikme = (
                bugun - son_teslim
            ).days

            if gecikme < 0:
                gecikme = 0

            return True, gecikme

        except sqlite3.Error:

            self.baglanti.rollback()
            raise

    def geciken_kitaplari_getir(self):

        self.imlec.execute("""
            SELECT
                kitaplar.kitap_adi,
                kitaplar.yazar,
                uyeler.ad_soyad,
                uyeler.telefon,
                oduncler.odunc_tarihi,
                oduncler.son_teslim_tarihi
            FROM oduncler

            JOIN kitaplar
                ON kitaplar.id = oduncler.kitap_id

            JOIN uyeler
                ON uyeler.id = oduncler.uye_id

            WHERE oduncler.durum = 'ODUNC'
              AND oduncler.son_teslim_tarihi < ?

            ORDER BY oduncler.son_teslim_tarihi
        """, (bugunun_tarihi(),))

        return self.imlec.fetchall()

    def uye_kitaplarini_getir(
        self,
        uye_id
    ):

        self.imlec.execute("""
            SELECT
                kitaplar.id AS kitap_id,
                kitaplar.kitap_adi,
                kitaplar.yazar,
                oduncler.odunc_tarihi,
                oduncler.son_teslim_tarihi
            FROM oduncler

            JOIN kitaplar
                ON kitaplar.id = oduncler.kitap_id

            WHERE oduncler.uye_id = ?
              AND oduncler.durum = 'ODUNC'

            ORDER BY oduncler.son_teslim_tarihi
        """, (uye_id,))

        return self.imlec.fetchall()

    def islem_gecmisini_getir(
        self,
        limit=30
    ):

        self.imlec.execute("""
            SELECT *
            FROM islemler
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

        return self.imlec.fetchall()

    def baglantiyi_kapat(self):

        if self.baglanti is not None:

            self.baglanti.close()
            self.baglanti = None


# --------------------------------------------------
# KÜTÜPHANE UYGULAMASI
# --------------------------------------------------

class KutuphanePro:

    def __init__(self):

        self.veritabani = (
            KutuphaneVeritabani()
        )

    def baslat(self):

        mesaj_yaz(
            "\nSQL Kütüphane Yönetim "
            "Sistemi başlatıldı."
        )

        while True:

            self.menuyu_goster()

            secim = menu_secimi_al()

            if secim == "1":
                self.kitaplari_goster()

            elif secim == "2":
                self.kitap_ara_menu()

            elif secim == "3":
                self.kitap_ekle_menu()

            elif secim == "4":
                self.kitap_sil_menu()

            elif secim == "5":
                self.uyeleri_goster()

            elif secim == "6":
                self.uye_ekle_menu()

            elif secim == "7":
                self.uye_sil_menu()

            elif secim == "8":
                self.odunc_ver_menu()

            elif secim == "9":
                self.iade_al_menu()

            elif secim == "10":
                self.gecikenleri_goster()

            elif secim == "11":
                self.uye_kitaplarini_goster()

            elif secim == "12":
                self.islem_gecmisini_goster()

            elif secim == "0":

                mesaj_yaz(
                    "\nKütüphane sistemi kapatılıyor."
                )

                break

            else:

                mesaj_yaz(
                    "\nGeçersiz menü seçimi."
                )

    @staticmethod
    def menuyu_goster():

        print("\n" + "=" * 60)
        print(
            "       SQL KÜTÜPHANE "
            "YÖNETİM SİSTEMİ PRO"
        )
        print("=" * 60)
        print("1  - Tüm kitapları göster")
        print("2  - Kitap ara")
        print("3  - Kitap ekle              🔒")
        print("4  - Kitap sil               🔒")
        print("5  - Tüm üyeleri göster")
        print("6  - Üye ekle                🔒")
        print("7  - Üye sil                 🔒")
        print("8  - Kitap ödünç ver         🔒")
        print("9  - Kitap iade al           🔒")
        print("10 - Geciken kitapları göster")
        print("11 - Üyenin aldığı kitaplar")
        print("12 - İşlem geçmişi           🔒")
        print("0  - Programı kapat")
        print("=" * 60)

    def kitaplari_goster(self):

        kitaplar = (
            self.veritabani
            .kitaplari_getir()
        )

        print("\n" + "=" * 75)
        print("                KİTAP LİSTESİ")
        print("=" * 75)

        if not kitaplar:

            mesaj_yaz(
                "Kayıtlı kitap bulunamadı."
            )

            return

        for kitap in kitaplar:

            print(
                f"\nKitap ID   : {kitap['id']}"
            )

            print(
                f"Kitap adı  : "
                f"{kitap['kitap_adi']}"
            )

            print(
                f"Yazar      : {kitap['yazar']}"
            )

            print(
                f"Kategori   : "
                f"{kitap['kategori']}"
            )

            print(
                f"ISBN       : {kitap['isbn']}"
            )

            print(
                f"Yayın yılı : "
                f"{kitap['yayin_yili']}"
            )

            print(
                f"Durum      : {kitap['durum']}"
            )

            print("-" * 75)

        seslendir(
            f"Toplam {len(kitaplar)} "
            "kitap bulundu."
        )

    def kitap_ara_menu(self):

        arama = input(
            "\nKitap adı, yazar, "
            "kategori veya ISBN: "
        ).strip()

        if not arama:

            mesaj_yaz(
                "\nArama metni boş olamaz."
            )

            return

        kitaplar = (
            self.veritabani.kitap_ara(
                arama
            )
        )

        if not kitaplar:

            mesaj_yaz(
                "\nKitap bulunamadı."
            )

            return

        for kitap in kitaplar:

            print(
                f"\nID: {kitap['id']} | "
                f"{kitap['kitap_adi']} | "
                f"{kitap['yazar']} | "
                f"{kitap['durum']}"
            )

        seslendir(
            f"{len(kitaplar)} kitap bulundu."
        )

    def kitap_ekle_menu(self):

        if not yonetici_sifresi_dogrula():
            return

        kitap_adi = input(
            "\nKitap adı: "
        ).strip()

        yazar = input(
            "Yazar: "
        ).strip()

        kategori = input(
            "Kategori: "
        ).strip()

        isbn = input(
            "ISBN: "
        ).replace(" ", "").strip()

        yayin_yili_metni = input(
            "Yayın yılı: "
        ).strip()

        if not all([
            kitap_adi,
            yazar,
            kategori,
            isbn
        ]):

            mesaj_yaz(
                "\nZorunlu alanlar boş olamaz."
            )

            return

        try:

            yayin_yili = (
                int(yayin_yili_metni)
                if yayin_yili_metni
                else None
            )

        except ValueError:

            mesaj_yaz(
                "\nYayın yılı sayı olmalıdır."
            )

            return

        basarili, kitap_id = (
            self.veritabani.kitap_ekle(
                kitap_adi,
                yazar,
                kategori,
                isbn,
                yayin_yili
            )
        )

        if not basarili:

            mesaj_yaz(
                "\nBu ISBN zaten kayıtlı."
            )

            return

        mesaj_yaz(
            f"\nKitap eklendi. "
            f"Kitap numarası {kitap_id}."
        )

    def kitap_sil_menu(self):

        if not yonetici_sifresi_dogrula():
            return

        try:

            kitap_id = int(
                input(
                    "\nSilinecek kitap ID: "
                )
            )

        except ValueError:

            mesaj_yaz(
                "\nKitap ID sayı olmalıdır."
            )

            return

        _, mesaj = (
            self.veritabani.kitap_sil(
                kitap_id
            )
        )

        mesaj_yaz(f"\n{mesaj}")

    def uyeleri_goster(self):

        uyeler = (
            self.veritabani
            .uyeleri_getir()
        )

        if not uyeler:

            mesaj_yaz(
                "\nAktif üye bulunamadı."
            )

            return

        for uye in uyeler:

            print(
                f"\nÜye ID      : {uye['id']}"
            )

            print(
                f"Ad soyad     : "
                f"{uye['ad_soyad']}"
            )

            print(
                f"Telefon      : "
                f"{uye['telefon']}"
            )

            print(
                f"E-posta      : "
                f"{uye['eposta']}"
            )

            print(
                f"Kayıt tarihi : "
                f"{uye['kayit_tarihi']}"
            )

            print("-" * 60)

        seslendir(
            f"{len(uyeler)} aktif üye bulundu."
        )

    def uye_ekle_menu(self):

        if not yonetici_sifresi_dogrula():
            return

        ad_soyad = input(
            "\nAd soyad: "
        ).strip()

        telefon = input(
            "Telefon: "
        ).strip()

        eposta = input(
            "E-posta: "
        ).strip().lower()

        if not ad_soyad:

            mesaj_yaz(
                "\nAd soyad boş olamaz."
            )

            return

        if not eposta:
            eposta = None

        basarili, uye_id = (
            self.veritabani.uye_ekle(
                ad_soyad,
                telefon,
                eposta
            )
        )

        if not basarili:

            mesaj_yaz(
                "\nBu e-posta zaten kayıtlı."
            )

            return

        mesaj_yaz(
            f"\nÜye eklendi. "
            f"Üye numarası {uye_id}."
        )

    def uye_sil_menu(self):

        if not yonetici_sifresi_dogrula():
            return

        try:

            uye_id = int(
                input(
                    "\nSilinecek üye ID: "
                )
            )

        except ValueError:

            mesaj_yaz(
                "\nÜye ID sayı olmalıdır."
            )

            return

        _, mesaj = (
            self.veritabani.uye_sil(
                uye_id
            )
        )

        mesaj_yaz(f"\n{mesaj}")

    def odunc_ver_menu(self):

        if not yonetici_sifresi_dogrula():
            return

        try:

            kitap_id = int(
                input(
                    "\nKitap ID: "
                )
            )

            uye_id = int(
                input(
                    "Üye ID: "
                )
            )

        except ValueError:

            mesaj_yaz(
                "\nID değerleri sayı olmalıdır."
            )

            return

        basarili, sonuc = (
            self.veritabani
            .kitap_odunc_ver(
                kitap_id,
                uye_id
            )
        )

        if not basarili:

            mesaj_yaz(f"\n{sonuc}")
            return

        mesaj_yaz(
            "\nKitap ödünç verildi. "
            f"Son teslim tarihi "
            f"{tarih_goster(sonuc)}."
        )

    def iade_al_menu(self):

        if not yonetici_sifresi_dogrula():
            return

        try:

            kitap_id = int(
                input(
                    "\nİade alınacak kitap ID: "
                )
            )

        except ValueError:

            mesaj_yaz(
                "\nKitap ID sayı olmalıdır."
            )

            return

        basarili, sonuc = (
            self.veritabani
            .kitap_iade_al(
                kitap_id
            )
        )

        if not basarili:

            mesaj_yaz(f"\n{sonuc}")
            return

        if sonuc > 0:

            mesaj_yaz(
                f"\nKitap iade alındı. "
                f"{sonuc} gün gecikmiş."
            )

        else:

            mesaj_yaz(
                "\nKitap zamanında iade edildi."
            )

    def gecikenleri_goster(self):

        kayitlar = (
            self.veritabani
            .geciken_kitaplari_getir()
        )

        if not kayitlar:

            mesaj_yaz(
                "\nGeciken kitap bulunamadı."
            )

            return

        bugun = datetime.now().date()

        for kayit in kayitlar:

            son_teslim = datetime.strptime(
                kayit["son_teslim_tarihi"],
                "%Y-%m-%d"
            ).date()

            gecikme = (
                bugun - son_teslim
            ).days

            print(
                f"\nKitap      : "
                f"{kayit['kitap_adi']}"
            )

            print(
                f"Yazar      : "
                f"{kayit['yazar']}"
            )

            print(
                f"Üye        : "
                f"{kayit['ad_soyad']}"
            )

            print(
                f"Telefon    : "
                f"{kayit['telefon']}"
            )

            print(
                f"Son teslim : "
                f"{tarih_goster(kayit['son_teslim_tarihi'])}"
            )

            print(
                f"Gecikme    : {gecikme} gün"
            )

            print("-" * 70)

        seslendir(
            f"{len(kayitlar)} "
            "geciken kitap bulundu."
        )

    def uye_kitaplarini_goster(self):

        try:

            uye_id = int(
                input(
                    "\nÜye ID: "
                )
            )

        except ValueError:

            mesaj_yaz(
                "\nÜye ID sayı olmalıdır."
            )

            return

        uye = self.veritabani.uye_bul(
            uye_id
        )

        if uye is None:

            mesaj_yaz(
                "\nÜye bulunamadı."
            )

            return

        kitaplar = (
            self.veritabani
            .uye_kitaplarini_getir(
                uye_id
            )
        )

        if not kitaplar:

            mesaj_yaz(
                "\nÜyenin üzerinde kitap yok."
            )

            return

        print(
            f"\nÜye: {uye['ad_soyad']}"
        )

        for kitap in kitaplar:

            print(
                f"\nKitap ID   : "
                f"{kitap['kitap_id']}"
            )

            print(
                f"Kitap adı  : "
                f"{kitap['kitap_adi']}"
            )

            print(
                f"Yazar      : "
                f"{kitap['yazar']}"
            )

            print(
                f"Alış tarihi: "
                f"{tarih_goster(kitap['odunc_tarihi'])}"
            )

            print(
                f"Son teslim : "
                f"{tarih_goster(kitap['son_teslim_tarihi'])}"
            )

            print("-" * 60)

        seslendir(
            f"Üyenin üzerinde "
            f"{len(kitaplar)} kitap bulunuyor."
        )

    def islem_gecmisini_goster(self):

        if not yonetici_sifresi_dogrula():
            return

        islemler = (
            self.veritabani
            .islem_gecmisini_getir(
                limit=30
            )
        )

        if not islemler:

            mesaj_yaz(
                "\nİşlem kaydı bulunamadı."
            )

            return

        for islem in islemler:

            print(
                f"\nİşlem ID   : "
                f"{islem['id']}"
            )

            print(
                f"İşlem türü : "
                f"{islem['islem_turu']}"
            )

            print(
                f"Açıklama   : "
                f"{islem['aciklama']}"
            )

            print(
                f"Tarih      : "
                f"{islem['tarih']}"
            )

            print("-" * 80)

        seslendir(
            f"{len(islemler)} "
            "işlem kaydı gösterildi."
        )


# --------------------------------------------------
# PROGRAMIN BAŞLANGIÇ NOKTASI
# --------------------------------------------------

def main():

    uygulama = None

    try:

        uygulama = KutuphanePro()
        uygulama.baslat()

    except KeyboardInterrupt:

        print(
            "\n\nProgram kullanıcı "
            "tarafından kapatıldı."
        )

    except sqlite3.Error as hata:

        print(
            "\nVeritabanı hatası oluştu:"
        )

        print(hata)

        seslendir(
            "Veritabanı hatası oluştu."
        )

    except (
        sd.PortAudioError,
        OSError
    ) as hata:

        print(
            "\nSes sistemi hatası oluştu:"
        )

        print(hata)

    finally:

        if uygulama is not None:

            uygulama.veritabani.baglantiyi_kapat()

        print(
            "\nProgram tamamen kapatıldı."
        )


if __name__ == "__main__":
    main()


# --------------------------------------------------
# PROGRAM SONU
# --------------------------------------------------