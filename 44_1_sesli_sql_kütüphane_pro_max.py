import sqlite3
import subprocess
import getpass
import tempfile
import os

from datetime import datetime

import sounddevice as sd
import speech_recognition as sr
from scipy.io.wavfile import write


# --------------------------------------------------
# SABİTLER
# --------------------------------------------------

VERITABANI_ADI = "kutuphane_44.db"
YONETICI_SIFRESI = "2580"

SES_KAYIT_SURESI = 5
ORNEKLEME_HIZI = 44100


# --------------------------------------------------
# YARDIMCI FONKSİYONLAR
# --------------------------------------------------

def tarih_al():
    return datetime.now().strftime(
        "%d.%m.%Y %H:%M:%S"
    )


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
# SESLİ KOMUT SİSTEMİ
# --------------------------------------------------

def sesli_komut_al():

    gecici_dosya = None

    try:

        print("\n🎙️ Konuşmaya başlayın.")
        print(
            f"{SES_KAYIT_SURESI} saniye "
            "boyunca dinleniyor..."
        )

        ses_kaydi = sd.rec(
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
            ses_kaydi
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

        mesaj_yaz(
            "\nSöylediğiniz anlaşılamadı."
        )

        return None

    except sr.RequestError as hata:

        print(
            "\nSes tanıma servisine "
            "ulaşılamadı:"
        )

        print(hata)

        seslendir(
            "Ses tanıma servisine ulaşılamadı."
        )

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

        seslendir(
            "Mikrofon hatası oluştu."
        )

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
        "kitap ekle": "1",
        "yeni kitap ekle": "1",

        "kitapları listele": "2",
        "kitapları göster": "2",
        "tüm kitaplar": "2",
        "listele": "2",

        "kitap ara": "3",
        "arama yap": "3",
        "ara": "3",

        "kitap sil": "4",
        "sil": "4",

        "kitap ödünç ver": "5",
        "ödünç ver": "5",

        "kitap teslim al": "6",
        "teslim al": "6",
        "iade al": "6",

        "işlem geçmişi": "7",
        "geçmişi göster": "7",
        "geçmiş": "7",

        "çıkış": "0",
        "programı kapat": "0",
        "kapat": "0"
    }

    if komut in komutlar:
        return komutlar[komut]

    for komut_metni, menu_numarasi in komutlar.items():

        if komut_metni in komut:
            return menu_numarasi

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

        self.baglanti.row_factory = sqlite3.Row

        self.imlec = self.baglanti.cursor()

        self.tablolari_olustur()
        self.ornek_kitaplari_olustur()

    def tablolari_olustur(self):

        self.imlec.execute("""
            CREATE TABLE IF NOT EXISTS kitaplar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kitap_adi TEXT NOT NULL,
                yazar TEXT NOT NULL,
                kategori TEXT NOT NULL,
                isbn TEXT UNIQUE NOT NULL,
                durum TEXT NOT NULL DEFAULT 'MUSAIT',
                alan_kisi TEXT,
                eklenme_tarihi TEXT NOT NULL,
                odunc_tarihi TEXT,
                teslim_tarihi TEXT
            )
        """)

        self.imlec.execute("""
            CREATE TABLE IF NOT EXISTS gecmis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                islem_turu TEXT NOT NULL,
                kitap_adi TEXT NOT NULL,
                aciklama TEXT NOT NULL,
                tarih TEXT NOT NULL
            )
        """)

        self.baglanti.commit()

    def ornek_kitaplari_olustur(self):

        self.imlec.execute("""
            SELECT COUNT(*) AS sayi
            FROM kitaplar
        """)

        sonuc = self.imlec.fetchone()

        if sonuc["sayi"] > 0:
            return

        kitaplar = [
            (
                "Python ile Programlama",
                "Ahmet Yılmaz",
                "Yazılım",
                "9780000000001",
                "MUSAIT",
                None,
                tarih_al(),
                None,
                None
            ),
            (
                "SQLite Veritabanı",
                "Mehmet Kaya",
                "Veritabanı",
                "9780000000002",
                "MUSAIT",
                None,
                tarih_al(),
                None,
                None
            ),
            (
                "Siber Güvenliğe Giriş",
                "Selin Demir",
                "Siber Güvenlik",
                "9780000000003",
                "MUSAIT",
                None,
                tarih_al(),
                None,
                None
            )
        ]

        self.imlec.executemany("""
            INSERT INTO kitaplar (
                kitap_adi,
                yazar,
                kategori,
                isbn,
                durum,
                alan_kisi,
                eklenme_tarihi,
                odunc_tarihi,
                teslim_tarihi
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, kitaplar)

        self.baglanti.commit()

    def gecmis_kaydet(
        self,
        islem_turu,
        kitap_adi,
        aciklama
    ):

        self.imlec.execute("""
            INSERT INTO gecmis (
                islem_turu,
                kitap_adi,
                aciklama,
                tarih
            )
            VALUES (?, ?, ?, ?)
        """, (
            islem_turu,
            kitap_adi,
            aciklama,
            tarih_al()
        ))

    def kitap_ekle(
        self,
        kitap_adi,
        yazar_adi,
        kategori,
        isbn
    ):

        try:

            self.imlec.execute("""
                INSERT INTO kitaplar (
                    kitap_adi,
                    yazar,
                    kategori,
                    isbn,
                    durum,
                    alan_kisi,
                    eklenme_tarihi,
                    odunc_tarihi,
                    teslim_tarihi
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                kitap_adi,
                yazar_adi,
                kategori,
                isbn,
                "MUSAIT",
                None,
                tarih_al(),
                None,
                None
            ))

            self.gecmis_kaydet(
                "KİTAP EKLENDİ",
                kitap_adi,
                (
                    f"{yazar_adi} tarafından "
                    "yazılan kitap sisteme eklendi."
                )
            )

            self.baglanti.commit()

            return True

        except sqlite3.IntegrityError:

            self.baglanti.rollback()

            return False

    def kitaplari_listele(self):

        self.imlec.execute("""
            SELECT *
            FROM kitaplar
            ORDER BY id
        """)

        return self.imlec.fetchall()

    def kitap_ara(self, arama_metni):

        arama = f"%{arama_metni}%"

        self.imlec.execute("""
            SELECT *
            FROM kitaplar
            WHERE kitap_adi LIKE ?
               OR yazar LIKE ?
               OR kategori LIKE ?
               OR isbn LIKE ?
            ORDER BY id
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

    def kitap_sil(self, silinecek_id):

        bulunan_kitap = self.kitap_bul(
            silinecek_id
        )

        if bulunan_kitap is None:

            return (
                False,
                "Bu ID numarasıyla kitap bulunamadı."
            )

        if bulunan_kitap["durum"] == "ODUNC":

            return (
                False,
                "Ödünçteki kitap silinemez."
            )

        kitap_adi = bulunan_kitap["kitap_adi"]

        self.imlec.execute("""
            DELETE FROM kitaplar
            WHERE id = ?
        """, (silinecek_id,))

        self.gecmis_kaydet(
            "KİTAP SİLİNDİ",
            kitap_adi,
            "Kitap sistemden silindi."
        )

        self.baglanti.commit()

        return (
            True,
            "Kitap başarıyla silindi."
        )

    def kitap_odunc_ver(
        self,
        kitap_id,
        alan_kisi
    ):

        bulunan_kitap = self.kitap_bul(
            kitap_id
        )

        if bulunan_kitap is None:

            return (
                False,
                "Kitap bulunamadı."
            )

        if bulunan_kitap["durum"] == "ODUNC":

            return (
                False,
                (
                    "Bu kitap zaten "
                    f"{bulunan_kitap['alan_kisi']} "
                    "adlı kişide."
                )
            )

        self.imlec.execute("""
            UPDATE kitaplar
            SET
                durum = ?,
                alan_kisi = ?,
                odunc_tarihi = ?,
                teslim_tarihi = ?
            WHERE id = ?
        """, (
            "ODUNC",
            alan_kisi,
            tarih_al(),
            None,
            kitap_id
        ))

        self.gecmis_kaydet(
            "ÖDÜNÇ VERİLDİ",
            bulunan_kitap["kitap_adi"],
            (
                f"Kitap {alan_kisi} adlı "
                "kişiye ödünç verildi."
            )
        )

        self.baglanti.commit()

        return (
            True,
            "Kitap başarıyla ödünç verildi."
        )

    def kitap_teslim_al(self, kitap_id):

        bulunan_kitap = self.kitap_bul(
            kitap_id
        )

        if bulunan_kitap is None:

            return (
                False,
                "Kitap bulunamadı."
            )

        if bulunan_kitap["durum"] != "ODUNC":

            return (
                False,
                "Bu kitap ödünçte görünmüyor."
            )

        alan_kisi = bulunan_kitap["alan_kisi"]

        self.imlec.execute("""
            UPDATE kitaplar
            SET
                durum = ?,
                alan_kisi = ?,
                teslim_tarihi = ?
            WHERE id = ?
        """, (
            "MUSAIT",
            None,
            tarih_al(),
            kitap_id
        ))

        self.gecmis_kaydet(
            "KİTAP TESLİM ALINDI",
            bulunan_kitap["kitap_adi"],
            (
                f"Kitap {alan_kisi} adlı "
                "kişiden teslim alındı."
            )
        )

        self.baglanti.commit()

        return (
            True,
            "Kitap başarıyla teslim alındı."
        )

    def gecmisi_listele(self, limit=30):

        self.imlec.execute("""
            SELECT *
            FROM gecmis
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

        return self.imlec.fetchall()

    def baglantiyi_kapat(self):

        if self.baglanti is not None:

            self.baglanti.close()
            self.baglanti = None


# --------------------------------------------------
# EKRANA YAZDIRMA FONKSİYONLARI
# --------------------------------------------------

def kitaplari_yazdir(kitaplar):

    if not kitaplar:

        mesaj_yaz(
            "\nKayıtlı kitap bulunamadı."
        )

        return

    print("\n" + "=" * 75)
    print("                     KİTAP LİSTESİ")
    print("=" * 75)

    for kayit in kitaplar:

        print(
            f"\nKitap ID      : {kayit['id']}"
        )

        print(
            f"Kitap adı     : "
            f"{kayit['kitap_adi']}"
        )

        print(
            f"Yazar         : {kayit['yazar']}"
        )

        print(
            f"Kategori      : "
            f"{kayit['kategori']}"
        )

        print(
            f"ISBN          : {kayit['isbn']}"
        )

        print(
            f"Durum         : {kayit['durum']}"
        )

        print(
            f"Alan kişi     : "
            f"{kayit['alan_kisi'] or '-'}"
        )

        print(
            f"Eklenme tarihi: "
            f"{kayit['eklenme_tarihi']}"
        )

        print(
            f"Ödünç tarihi  : "
            f"{kayit['odunc_tarihi'] or '-'}"
        )

        print(
            f"Teslim tarihi : "
            f"{kayit['teslim_tarihi'] or '-'}"
        )

        print("-" * 75)

    seslendir(
        f"Toplam {len(kitaplar)} kitap gösterildi."
    )


def gecmisi_yazdir(islemler):

    if not islemler:

        mesaj_yaz(
            "\nİşlem geçmişi bulunamadı."
        )

        return

    print("\n" + "=" * 80)
    print("                    İŞLEM GEÇMİŞİ")
    print("=" * 80)

    for kayit in islemler:

        print(
            f"\nİşlem ID   : {kayit['id']}"
        )

        print(
            f"İşlem türü : "
            f"{kayit['islem_turu']}"
        )

        print(
            f"Kitap      : "
            f"{kayit['kitap_adi']}"
        )

        print(
            f"Açıklama   : "
            f"{kayit['aciklama']}"
        )

        print(
            f"Tarih      : {kayit['tarih']}"
        )

        print("-" * 80)

    seslendir(
        f"Son {len(islemler)} işlem gösterildi."
    )


# --------------------------------------------------
# KÜTÜPHANE UYGULAMASI
# --------------------------------------------------

class SesliKutuphanePro:

    def __init__(self):

        self.veritabani = (
            KutuphaneVeritabani()
        )

    @staticmethod
    def menuyu_goster():

        print("\n" + "=" * 60)
        print(
            "       44 - SESLİ SQL "
            "KÜTÜPHANE PRO MAX"
        )
        print("=" * 60)
        print("1 - Kitap ekle                 🔒")
        print("2 - Kitapları listele")
        print("3 - Kitap ara")
        print("4 - Kitap sil                  🔒")
        print("5 - Kitap ödünç ver            🔒")
        print("6 - Kitap teslim al            🔒")
        print("7 - İşlem geçmişi              🔒")
        print("0 - Programı kapat")
        print("=" * 60)

    def baslat(self):

        mesaj_yaz(
            "\nSesli SQL Kütüphane "
            "Sistemi başlatıldı."
        )

        while True:

            self.menuyu_goster()

            secim = menu_secimi_al()

            if secim == "1":
                self.kitap_ekle_menu()

            elif secim == "2":
                self.kitaplari_listele_menu()

            elif secim == "3":
                self.kitap_ara_menu()

            elif secim == "4":
                self.kitap_sil_menu()

            elif secim == "5":
                self.odunc_ver_menu()

            elif secim == "6":
                self.teslim_al_menu()

            elif secim == "7":
                self.gecmis_menu()

            elif secim == "0":

                mesaj_yaz(
                    "\nKütüphane sistemi kapatılıyor."
                )

                break

            else:

                mesaj_yaz(
                    "\nGeçersiz menü seçimi."
                )

    def kitap_ekle_menu(self):

        if not yonetici_sifresi_dogrula():
            return

        kitap_adi = input(
            "\nKitap adı: "
        ).strip()

        yazar_adi = input(
            "Yazar adı: "
        ).strip()

        kategori = input(
            "Kategori: "
        ).strip()

        isbn = input(
            "ISBN numarası: "
        ).replace(" ", "").strip()

        if not all([
            kitap_adi,
            yazar_adi,
            kategori,
            isbn
        ]):

            mesaj_yaz(
                "\nBilgiler boş bırakılamaz."
            )

            return

        basarili = (
            self.veritabani.kitap_ekle(
                kitap_adi,
                yazar_adi,
                kategori,
                isbn
            )
        )

        if basarili:

            mesaj_yaz(
                "\nKitap başarıyla eklendi."
            )

        else:

            mesaj_yaz(
                "\nBu ISBN numarası "
                "zaten kayıtlı."
            )

    def kitaplari_listele_menu(self):

        kitaplar = (
            self.veritabani
            .kitaplari_listele()
        )

        kitaplari_yazdir(
            kitaplar
        )

    def kitap_ara_menu(self):

        arama_metni = input(
            "\nKitap, yazar, kategori "
            "veya ISBN: "
        ).strip()

        if not arama_metni:

            mesaj_yaz(
                "\nArama metni boş bırakılamaz."
            )

            return

        sonuclar = (
            self.veritabani.kitap_ara(
                arama_metni
            )
        )

        kitaplari_yazdir(
            sonuclar
        )

    def kitap_sil_menu(self):

        if not yonetici_sifresi_dogrula():
            return

        try:

            silinecek_id = int(
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
                silinecek_id
            )
        )

        mesaj_yaz(
            f"\n{mesaj}"
        )

    def odunc_ver_menu(self):

        if not yonetici_sifresi_dogrula():
            return

        try:

            kitap_id = int(
                input(
                    "\nÖdünç verilecek kitap ID: "
                )
            )

        except ValueError:

            mesaj_yaz(
                "\nKitap ID sayı olmalıdır."
            )

            return

        alan_kisi = input(
            "Kitabı alan kişinin adı: "
        ).strip()

        if not alan_kisi:

            mesaj_yaz(
                "\nKişi adı boş bırakılamaz."
            )

            return

        _, mesaj = (
            self.veritabani
            .kitap_odunc_ver(
                kitap_id,
                alan_kisi
            )
        )

        mesaj_yaz(
            f"\n{mesaj}"
        )

    def teslim_al_menu(self):

        if not yonetici_sifresi_dogrula():
            return

        try:

            kitap_id = int(
                input(
                    "\nTeslim alınacak kitap ID: "
                )
            )

        except ValueError:

            mesaj_yaz(
                "\nKitap ID sayı olmalıdır."
            )

            return

        _, mesaj = (
            self.veritabani
            .kitap_teslim_al(
                kitap_id
            )
        )

        mesaj_yaz(
            f"\n{mesaj}"
        )

    def gecmis_menu(self):

        if not yonetici_sifresi_dogrula():
            return

        islemler = (
            self.veritabani
            .gecmisi_listele(
                limit=30
            )
        )

        gecmisi_yazdir(
            islemler
        )


# --------------------------------------------------
# PROGRAMIN BAŞLANGIÇ NOKTASI
# --------------------------------------------------

def main():

    uygulama = None

    try:

        uygulama = SesliKutuphanePro()
        uygulama.baslat()

    except KeyboardInterrupt:

        print(
            "\n\nProgram kullanıcı "
            "tarafından kapatıldı."
        )

        seslendir(
            "Program kapatıldı."
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