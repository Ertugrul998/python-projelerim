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

VERITABANI_ADI = "gorev_takip_45.db"
YONETICI_SIFRESI = "2580"

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


def tarihi_duzenle(tarih_metni):

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


def tarih_gecerli_mi(tarih_metni):

    try:

        datetime.strptime(
            tarih_metni,
            "%Y-%m-%d"
        )

        return True

    except ValueError:
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
        "görev ekle": "1",
        "yeni görev ekle": "1",

        "görevleri listele": "2",
        "görevleri göster": "2",
        "tüm görevler": "2",
        "listele": "2",

        "görev ara": "3",
        "arama yap": "3",

        "görevi tamamla": "4",
        "tamamlandı yap": "4",
        "görev tamamla": "4",

        "görev sil": "5",
        "görevi sil": "5",

        "bekleyen görevler": "6",
        "bekleyenleri göster": "6",

        "tamamlanan görevler": "7",
        "tamamlananları göster": "7",

        "geciken görevler": "8",
        "gecikenleri göster": "8",

        "işlem geçmişi": "9",
        "geçmişi göster": "9",
        "geçmiş": "9",

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

class GorevVeritabani:

    def __init__(self):

        self.baglanti = sqlite3.connect(
            VERITABANI_ADI
        )

        self.baglanti.row_factory = sqlite3.Row

        self.imlec = self.baglanti.cursor()

        self.tablolari_olustur()

    def tablolari_olustur(self):

        self.imlec.execute("""
            CREATE TABLE IF NOT EXISTS gorevler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                baslik TEXT NOT NULL,
                aciklama TEXT NOT NULL,
                oncelik TEXT NOT NULL,
                durum TEXT NOT NULL DEFAULT 'BEKLIYOR',
                son_teslim_tarihi TEXT,
                olusturma_tarihi TEXT NOT NULL,
                tamamlanma_tarihi TEXT
            )
        """)

        self.imlec.execute("""
            CREATE TABLE IF NOT EXISTS gecmis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                islem_turu TEXT NOT NULL,
                gorev_basligi TEXT NOT NULL,
                aciklama TEXT NOT NULL,
                tarih TEXT NOT NULL
            )
        """)

        self.baglanti.commit()

    def gecmis_kaydet(
        self,
        islem_turu,
        gorev_basligi,
        aciklama
    ):

        self.imlec.execute("""
            INSERT INTO gecmis (
                islem_turu,
                gorev_basligi,
                aciklama,
                tarih
            )
            VALUES (?, ?, ?, ?)
        """, (
            islem_turu,
            gorev_basligi,
            aciklama,
            tarih_saat_al()
        ))

    def gorev_ekle(
        self,
        baslik,
        aciklama,
        oncelik,
        son_teslim_tarihi
    ):

        try:

            self.imlec.execute("""
                INSERT INTO gorevler (
                    baslik,
                    aciklama,
                    oncelik,
                    durum,
                    son_teslim_tarihi,
                    olusturma_tarihi,
                    tamamlanma_tarihi
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                baslik,
                aciklama,
                oncelik,
                "BEKLIYOR",
                son_teslim_tarihi,
                tarih_saat_al(),
                None
            ))

            gorev_id = self.imlec.lastrowid

            self.gecmis_kaydet(
                "GÖREV EKLENDİ",
                baslik,
                (
                    f"{oncelik} öncelikli "
                    "yeni görev oluşturuldu."
                )
            )

            self.baglanti.commit()

            return True, gorev_id

        except sqlite3.Error:

            self.baglanti.rollback()
            raise

    def gorevleri_listele(self):

        self.imlec.execute("""
            SELECT *
            FROM gorevler

            ORDER BY
                CASE oncelik
                    WHEN 'YÜKSEK' THEN 1
                    WHEN 'ORTA' THEN 2
                    WHEN 'DÜŞÜK' THEN 3
                    ELSE 4
                END,
                id DESC
        """)

        return self.imlec.fetchall()

    def gorev_bul(self, gorev_id):

        self.imlec.execute("""
            SELECT *
            FROM gorevler
            WHERE id = ?
        """, (gorev_id,))

        return self.imlec.fetchone()

    def gorev_ara(self, arama_metni):

        arama = f"%{arama_metni}%"

        self.imlec.execute("""
            SELECT *
            FROM gorevler
            WHERE baslik LIKE ?
               OR aciklama LIKE ?
               OR oncelik LIKE ?
               OR durum LIKE ?
            ORDER BY id DESC
        """, (
            arama,
            arama,
            arama,
            arama
        ))

        return self.imlec.fetchall()

    def gorevi_tamamla(self, gorev_id):

        gorev = self.gorev_bul(
            gorev_id
        )

        if gorev is None:

            return (
                False,
                "Bu ID numarasıyla görev bulunamadı."
            )

        if gorev["durum"] == "TAMAMLANDI":

            return (
                False,
                "Bu görev zaten tamamlanmış."
            )

        self.imlec.execute("""
            UPDATE gorevler
            SET
                durum = ?,
                tamamlanma_tarihi = ?
            WHERE id = ?
        """, (
            "TAMAMLANDI",
            tarih_saat_al(),
            gorev_id
        ))

        self.gecmis_kaydet(
            "GÖREV TAMAMLANDI",
            gorev["baslik"],
            "Görev tamamlandı olarak işaretlendi."
        )

        self.baglanti.commit()

        return (
            True,
            "Görev tamamlandı olarak işaretlendi."
        )

    def gorev_sil(self, gorev_id):

        gorev = self.gorev_bul(
            gorev_id
        )

        if gorev is None:

            return (
                False,
                "Bu ID numarasıyla görev bulunamadı."
            )

        self.imlec.execute("""
            DELETE FROM gorevler
            WHERE id = ?
        """, (gorev_id,))

        self.gecmis_kaydet(
            "GÖREV SİLİNDİ",
            gorev["baslik"],
            "Görev sistemden tamamen silindi."
        )

        self.baglanti.commit()

        return (
            True,
            "Görev başarıyla silindi."
        )

    def bekleyen_gorevleri_getir(self):

        self.imlec.execute("""
            SELECT *
            FROM gorevler
            WHERE durum = 'BEKLIYOR'
            ORDER BY id DESC
        """)

        return self.imlec.fetchall()

    def tamamlanan_gorevleri_getir(self):

        self.imlec.execute("""
            SELECT *
            FROM gorevler
            WHERE durum = 'TAMAMLANDI'
            ORDER BY id DESC
        """)

        return self.imlec.fetchall()

    def geciken_gorevleri_getir(self):

        self.imlec.execute("""
            SELECT *
            FROM gorevler
            WHERE durum = 'BEKLIYOR'
              AND son_teslim_tarihi IS NOT NULL
              AND son_teslim_tarihi < ?
            ORDER BY son_teslim_tarihi
        """, (bugunun_tarihi(),))

        return self.imlec.fetchall()

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

def gorevleri_yazdir(gorevler, baslik):

    if not gorevler:

        mesaj_yaz(
            "\nGörev kaydı bulunamadı."
        )

        return

    print("\n" + "=" * 80)
    print(f"{baslik:^80}")
    print("=" * 80)

    for gorev in gorevler:

        print(
            f"\nGörev ID          : {gorev['id']}"
        )

        print(
            f"Başlık            : {gorev['baslik']}"
        )

        print(
            f"Açıklama          : {gorev['aciklama']}"
        )

        print(
            f"Öncelik           : {gorev['oncelik']}"
        )

        print(
            f"Durum             : {gorev['durum']}"
        )

        print(
            f"Son teslim tarihi : "
            f"{tarihi_duzenle(gorev['son_teslim_tarihi'])}"
        )

        print(
            f"Oluşturma tarihi  : "
            f"{gorev['olusturma_tarihi']}"
        )

        print(
            f"Tamamlanma tarihi : "
            f"{gorev['tamamlanma_tarihi'] or '-'}"
        )

        print("-" * 80)

    seslendir(
        f"Toplam {len(gorevler)} görev gösterildi."
    )


def gecmisi_yazdir(islemler):

    if not islemler:

        mesaj_yaz(
            "\nİşlem geçmişi bulunamadı."
        )

        return

    print("\n" + "=" * 80)
    print(f"{'İŞLEM GEÇMİŞİ':^80}")
    print("=" * 80)

    for islem in islemler:

        print(
            f"\nİşlem ID   : {islem['id']}"
        )

        print(
            f"İşlem türü : {islem['islem_turu']}"
        )

        print(
            f"Görev      : {islem['gorev_basligi']}"
        )

        print(
            f"Açıklama   : {islem['aciklama']}"
        )

        print(
            f"Tarih      : {islem['tarih']}"
        )

        print("-" * 80)

    seslendir(
        f"Son {len(islemler)} işlem gösterildi."
    )


# --------------------------------------------------
# GÖREV TAKİP UYGULAMASI
# --------------------------------------------------

class SesliGorevTakipPro:

    def __init__(self):

        self.veritabani = GorevVeritabani()

    @staticmethod
    def menuyu_goster():

        print("\n" + "=" * 62)
        print(
            "       45 - SESLİ SQL GÖREV TAKİP SİSTEMİ"
        )
        print("=" * 62)
        print("1 - Yeni görev ekle             🔒")
        print("2 - Tüm görevleri listele")
        print("3 - Görev ara")
        print("4 - Görevi tamamlandı yap       🔒")
        print("5 - Görev sil                   🔒")
        print("6 - Bekleyen görevleri göster")
        print("7 - Tamamlanan görevleri göster")
        print("8 - Geciken görevleri göster")
        print("9 - İşlem geçmişi               🔒")
        print("0 - Programı kapat")
        print("=" * 62)

    def baslat(self):

        mesaj_yaz(
            "\nSesli SQL Görev Takip "
            "Sistemi başlatıldı."
        )

        while True:

            self.menuyu_goster()

            secim = menu_secimi_al()

            if secim == "1":
                self.gorev_ekle_menu()

            elif secim == "2":
                self.tum_gorevler_menu()

            elif secim == "3":
                self.gorev_ara_menu()

            elif secim == "4":
                self.gorev_tamamla_menu()

            elif secim == "5":
                self.gorev_sil_menu()

            elif secim == "6":
                self.bekleyen_gorevler_menu()

            elif secim == "7":
                self.tamamlanan_gorevler_menu()

            elif secim == "8":
                self.geciken_gorevler_menu()

            elif secim == "9":
                self.gecmis_menu()

            elif secim == "0":

                mesaj_yaz(
                    "\nGörev takip sistemi kapatılıyor."
                )

                break

            else:

                mesaj_yaz(
                    "\nGeçersiz menü seçimi."
                )

    def gorev_ekle_menu(self):

        if not yonetici_sifresi_dogrula():
            return

        baslik = input(
            "\nGörev başlığı: "
        ).strip()

        aciklama = input(
            "Görev açıklaması: "
        ).strip()

        print("\nÖncelik seçiniz:")
        print("1 - Düşük")
        print("2 - Orta")
        print("3 - Yüksek")

        oncelik_secimi = input(
            "Öncelik: "
        ).strip()

        oncelikler = {
            "1": "DÜŞÜK",
            "2": "ORTA",
            "3": "YÜKSEK"
        }

        oncelik = oncelikler.get(
            oncelik_secimi
        )

        if oncelik is None:

            mesaj_yaz(
                "\nGeçersiz öncelik seçimi."
            )

            return

        son_teslim = input(
            "Son teslim tarihi "
            "(YYYY-AA-GG, boş bırakılabilir): "
        ).strip()

        if not baslik or not aciklama:

            mesaj_yaz(
                "\nBaşlık ve açıklama "
                "boş bırakılamaz."
            )

            return

        if son_teslim:

            if not tarih_gecerli_mi(
                son_teslim
            ):

                mesaj_yaz(
                    "\nTarih YYYY-AA-GG "
                    "biçiminde olmalıdır."
                )

                return

        else:
            son_teslim = None

        _, gorev_id = (
            self.veritabani.gorev_ekle(
                baslik,
                aciklama,
                oncelik,
                son_teslim
            )
        )

        mesaj_yaz(
            f"\nGörev başarıyla eklendi. "
            f"Görev numarası {gorev_id}."
        )

    def tum_gorevler_menu(self):

        gorevler = (
            self.veritabani
            .gorevleri_listele()
        )

        gorevleri_yazdir(
            gorevler,
            "TÜM GÖREVLER"
        )

    def gorev_ara_menu(self):

        arama_metni = input(
            "\nAranacak görev: "
        ).strip()

        if not arama_metni:

            mesaj_yaz(
                "\nArama metni boş bırakılamaz."
            )

            return

        gorevler = (
            self.veritabani.gorev_ara(
                arama_metni
            )
        )

        gorevleri_yazdir(
            gorevler,
            "ARAMA SONUÇLARI"
        )

    def gorev_tamamla_menu(self):

        if not yonetici_sifresi_dogrula():
            return

        try:

            gorev_id = int(
                input(
                    "\nTamamlanacak görev ID: "
                )
            )

        except ValueError:

            mesaj_yaz(
                "\nGörev ID sayı olmalıdır."
            )

            return

        _, mesaj = (
            self.veritabani
            .gorevi_tamamla(
                gorev_id
            )
        )

        mesaj_yaz(
            f"\n{mesaj}"
        )

    def gorev_sil_menu(self):

        if not yonetici_sifresi_dogrula():
            return

        try:

            gorev_id = int(
                input(
                    "\nSilinecek görev ID: "
                )
            )

        except ValueError:

            mesaj_yaz(
                "\nGörev ID sayı olmalıdır."
            )

            return

        _, mesaj = (
            self.veritabani.gorev_sil(
                gorev_id
            )
        )

        mesaj_yaz(
            f"\n{mesaj}"
        )

    def bekleyen_gorevler_menu(self):

        gorevler = (
            self.veritabani
            .bekleyen_gorevleri_getir()
        )

        gorevleri_yazdir(
            gorevler,
            "BEKLEYEN GÖREVLER"
        )

    def tamamlanan_gorevler_menu(self):

        gorevler = (
            self.veritabani
            .tamamlanan_gorevleri_getir()
        )

        gorevleri_yazdir(
            gorevler,
            "TAMAMLANAN GÖREVLER"
        )

    def geciken_gorevler_menu(self):

        gorevler = (
            self.veritabani
            .geciken_gorevleri_getir()
        )

        gorevleri_yazdir(
            gorevler,
            "GECİKEN GÖREVLER"
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

        uygulama = SesliGorevTakipPro()
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