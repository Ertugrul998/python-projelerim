import getpass
import hashlib
import sqlite3
import subprocess
from datetime import datetime


VERITABANI_ADI = "banka_41.db"
DING_SESI = "/System/Library/Sounds/Glass.aiff"

VARSAYILAN_KULLANICI = "ertugrul"
VARSAYILAN_SIFRE = "2580"
VARSAYILAN_BAKIYE = 10000.0


def seslendir(metin):
    """
    macOS seslendirmesini arka planda çalıştırır.
    Program sesin bitmesini beklemez.
    """
    try:
        subprocess.Popen(
            ["say", metin],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except OSError:
        pass


def ding_cal():
    """
    macOS ding sesini arka planda çalar.
    """
    try:
        subprocess.Popen(
            ["afplay", DING_SESI],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except OSError:
        pass


def sifre_hashle(sifre):
    return hashlib.sha256(
        sifre.encode("utf-8")
    ).hexdigest()


class BankaVeritabani:
    def __init__(self, dosya_adi):
        self.baglanti = sqlite3.connect(
            dosya_adi,
            timeout=10
        )

        self.imlec = self.baglanti.cursor()

        # Veritabanının kilitlenme ihtimalini azaltır.
        self.imlec.execute("PRAGMA journal_mode=WAL")
        self.imlec.execute("PRAGMA busy_timeout=10000")
        self.imlec.execute("PRAGMA foreign_keys=ON")

        self.hesaplar_tablosunu_olustur()
        self.islemler_tablosunu_olustur()
        self.varsayilan_hesaplari_olustur()

    def hesaplar_tablosunu_olustur(self):
        self.imlec.execute(
            """
            CREATE TABLE IF NOT EXISTS hesaplar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_adi TEXT UNIQUE NOT NULL,
                sifre TEXT NOT NULL,
                bakiye REAL NOT NULL DEFAULT 0,
                olusturma_tarihi TEXT NOT NULL
            )
            """
        )

        self.baglanti.commit()

    def islemler_tablosunu_olustur(self):
        self.imlec.execute(
            """
            CREATE TABLE IF NOT EXISTS islemler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hesap_id INTEGER NOT NULL,
                islem_turu TEXT NOT NULL,
                miktar REAL NOT NULL,
                aciklama TEXT NOT NULL,
                tarih TEXT NOT NULL,

                FOREIGN KEY (hesap_id)
                REFERENCES hesaplar(id)
                ON DELETE CASCADE
            )
            """
        )

        self.baglanti.commit()

    def varsayilan_hesaplari_olustur(self):
        """
        Transferi deneyebilmek için iki örnek hesap oluşturur.

        ertugrul / 2580
        ayaz / 1234
        """
        hesaplar = [
            (
                VARSAYILAN_KULLANICI,
                VARSAYILAN_SIFRE,
                VARSAYILAN_BAKIYE
            ),
            (
                "ayaz",
                "1234",
                5000.0
            )
        ]

        tarih = datetime.now().strftime(
            "%d.%m.%Y %H:%M:%S"
        )

        for kullanici_adi, sifre, bakiye in hesaplar:
            try:
                self.imlec.execute(
                    """
                    INSERT INTO hesaplar (
                        kullanici_adi,
                        sifre,
                        bakiye,
                        olusturma_tarihi
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        kullanici_adi,
                        sifre_hashle(sifre),
                        bakiye,
                        tarih
                    )
                )

            except sqlite3.IntegrityError:
                # Hesap zaten varsa yeniden oluşturulmaz.
                pass

        self.baglanti.commit()

    def hesap_olustur(
        self,
        kullanici_adi,
        sifre,
        baslangic_bakiyesi
    ):
        kullanici_adi = kullanici_adi.strip().lower()

        if not kullanici_adi or not sifre:
            return False, "Kullanıcı adı ve şifre boş bırakılamaz."

        if baslangic_bakiyesi < 0:
            return False, "Başlangıç bakiyesi negatif olamaz."

        tarih = datetime.now().strftime(
            "%d.%m.%Y %H:%M:%S"
        )

        try:
            self.imlec.execute(
                """
                INSERT INTO hesaplar (
                    kullanici_adi,
                    sifre,
                    bakiye,
                    olusturma_tarihi
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    kullanici_adi,
                    sifre_hashle(sifre),
                    baslangic_bakiyesi,
                    tarih
                )
            )

            self.baglanti.commit()

            return True, "Hesap başarıyla oluşturuldu."

        except sqlite3.IntegrityError:
            return False, "Bu kullanıcı adı zaten kayıtlı."

        except sqlite3.Error:
            self.baglanti.rollback()
            return False, "Hesap oluşturulurken hata oluştu."

    def giris_yap(self, kullanici_adi, sifre):
        self.imlec.execute(
            """
            SELECT id, kullanici_adi, bakiye
            FROM hesaplar
            WHERE kullanici_adi = ?
            AND sifre = ?
            """,
            (
                kullanici_adi.strip().lower(),
                sifre_hashle(sifre)
            )
        )

        return self.imlec.fetchone()

    def bakiye_getir(self, hesap_id):
        self.imlec.execute(
            """
            SELECT bakiye
            FROM hesaplar
            WHERE id = ?
            """,
            (hesap_id,)
        )

        sonuc = self.imlec.fetchone()

        if sonuc is None:
            return None

        return float(sonuc[0])

    def kullanici_adi_getir(self, hesap_id):
        self.imlec.execute(
            """
            SELECT kullanici_adi
            FROM hesaplar
            WHERE id = ?
            """,
            (hesap_id,)
        )

        sonuc = self.imlec.fetchone()

        if sonuc is None:
            return None

        return sonuc[0]

    def islem_kaydet(
        self,
        hesap_id,
        islem_turu,
        miktar,
        aciklama,
        commit=True
    ):
        tarih = datetime.now().strftime(
            "%d.%m.%Y %H:%M:%S"
        )

        self.imlec.execute(
            """
            INSERT INTO islemler (
                hesap_id,
                islem_turu,
                miktar,
                aciklama,
                tarih
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                hesap_id,
                islem_turu,
                miktar,
                aciklama,
                tarih
            )
        )

        if commit:
            self.baglanti.commit()

    def para_yatir(self, hesap_id, miktar):
        if miktar <= 0:
            return False, "Yatırılacak miktar sıfırdan büyük olmalı."

        try:
            self.imlec.execute(
                """
                UPDATE hesaplar
                SET bakiye = bakiye + ?
                WHERE id = ?
                """,
                (miktar, hesap_id)
            )

            if self.imlec.rowcount == 0:
                self.baglanti.rollback()
                return False, "Hesap bulunamadı."

            self.islem_kaydet(
                hesap_id,
                "Para yatırma",
                miktar,
                f"{miktar:.2f} TL hesaba yatırıldı",
                commit=False
            )

            self.baglanti.commit()

            return True, "Para yatırma işlemi başarılı."

        except sqlite3.Error:
            self.baglanti.rollback()
            return False, "Para yatırılırken hata oluştu."

    def para_cek(self, hesap_id, miktar):
        if miktar <= 0:
            return False, "Çekilecek miktar sıfırdan büyük olmalı."

        bakiye = self.bakiye_getir(hesap_id)

        if bakiye is None:
            return False, "Hesap bulunamadı."

        if miktar > bakiye:
            self.islem_kaydet(
                hesap_id,
                "Başarısız para çekme",
                miktar,
                "Yetersiz bakiye nedeniyle işlem reddedildi"
            )

            return False, "Yetersiz bakiye."

        try:
            self.imlec.execute(
                """
                UPDATE hesaplar
                SET bakiye = bakiye - ?
                WHERE id = ?
                """,
                (miktar, hesap_id)
            )

            self.islem_kaydet(
                hesap_id,
                "Para çekme",
                miktar,
                f"{miktar:.2f} TL hesaptan çekildi",
                commit=False
            )

            self.baglanti.commit()

            return True, "Para çekme işlemi başarılı."

        except sqlite3.Error:
            self.baglanti.rollback()
            return False, "Para çekilirken hata oluştu."

    def para_transferi(
        self,
        gonderen_id,
        alici_kullanici_adi,
        miktar
    ):
        alici_kullanici_adi = (
            alici_kullanici_adi.strip().lower()
        )

        if miktar <= 0:
            return False, "Transfer miktarı sıfırdan büyük olmalı."

        self.imlec.execute(
            """
            SELECT id, kullanici_adi
            FROM hesaplar
            WHERE kullanici_adi = ?
            """,
            (alici_kullanici_adi,)
        )

        alici = self.imlec.fetchone()

        if alici is None:
            return False, "Alıcı hesap bulunamadı."

        alici_id, alici_adi = alici

        if alici_id == gonderen_id:
            return False, "Kendi hesabına transfer yapamazsın."

        gonderen_bakiye = self.bakiye_getir(gonderen_id)

        if gonderen_bakiye is None:
            return False, "Gönderen hesap bulunamadı."

        if miktar > gonderen_bakiye:
            return False, "Transfer için bakiye yetersiz."

        gonderen_adi = self.kullanici_adi_getir(
            gonderen_id
        )

        try:
            self.imlec.execute("BEGIN IMMEDIATE")

            self.imlec.execute(
                """
                UPDATE hesaplar
                SET bakiye = bakiye - ?
                WHERE id = ?
                """,
                (miktar, gonderen_id)
            )

            self.imlec.execute(
                """
                UPDATE hesaplar
                SET bakiye = bakiye + ?
                WHERE id = ?
                """,
                (miktar, alici_id)
            )

            self.islem_kaydet(
                gonderen_id,
                "Giden transfer",
                miktar,
                f"{alici_adi} hesabına transfer yapıldı",
                commit=False
            )

            self.islem_kaydet(
                alici_id,
                "Gelen transfer",
                miktar,
                f"{gonderen_adi} hesabından transfer geldi",
                commit=False
            )

            self.baglanti.commit()

            return True, "Para transferi başarıyla tamamlandı."

        except sqlite3.Error:
            self.baglanti.rollback()
            return False, "Transfer sırasında hata oluştu."

    def islem_gecmisini_getir(self, hesap_id):
        self.imlec.execute(
            """
            SELECT
                islem_turu,
                miktar,
                aciklama,
                tarih
            FROM islemler
            WHERE hesap_id = ?
            ORDER BY id DESC
            """,
            (hesap_id,)
        )

        return self.imlec.fetchall()

    def sifre_degistir(
        self,
        hesap_id,
        eski_sifre,
        yeni_sifre
    ):
        self.imlec.execute(
            """
            SELECT id
            FROM hesaplar
            WHERE id = ?
            AND sifre = ?
            """,
            (
                hesap_id,
                sifre_hashle(eski_sifre)
            )
        )

        hesap = self.imlec.fetchone()

        if hesap is None:
            return False, "Eski şifre yanlış."

        if len(yeni_sifre) < 4:
            return False, "Yeni şifre en az 4 karakter olmalı."

        try:
            self.imlec.execute(
                """
                UPDATE hesaplar
                SET sifre = ?
                WHERE id = ?
                """,
                (
                    sifre_hashle(yeni_sifre),
                    hesap_id
                )
            )

            self.baglanti.commit()

            return True, "Şifre başarıyla değiştirildi."

        except sqlite3.Error:
            self.baglanti.rollback()
            return False, "Şifre değiştirilirken hata oluştu."

    def hesabi_sil(self, hesap_id, sifre):
        self.imlec.execute(
            """
            SELECT bakiye
            FROM hesaplar
            WHERE id = ?
            AND sifre = ?
            """,
            (
                hesap_id,
                sifre_hashle(sifre)
            )
        )

        hesap = self.imlec.fetchone()

        if hesap is None:
            return False, "Şifre yanlış."

        bakiye = float(hesap[0])

        if bakiye != 0:
            return (
                False,
                "Hesabı silmeden önce bakiye sıfır olmalı."
            )

        try:
            self.imlec.execute(
                """
                DELETE FROM hesaplar
                WHERE id = ?
                """,
                (hesap_id,)
            )

            self.baglanti.commit()

            return True, "Hesap başarıyla silindi."

        except sqlite3.Error:
            self.baglanti.rollback()
            return False, "Hesap silinirken hata oluştu."

    def kapat(self):
        if self.baglanti:
            self.baglanti.close()


class BankaUygulamasi:
    def __init__(self):
        self.veritabani = BankaVeritabani(
            VERITABANI_ADI
        )

        self.aktif_hesap_id = None
        self.aktif_kullanici_adi = None

    def yeni_hesap_olustur(self):
        print("\n========= YENİ HESAP OLUŞTUR =========")

        kullanici_adi = input(
            "Yeni kullanıcı adı: "
        ).strip().lower()

        sifre = getpass.getpass(
            "Yeni şifre: "
        )

        sifre_tekrar = getpass.getpass(
            "Yeni şifreyi tekrar gir: "
        )

        if sifre != sifre_tekrar:
            print("Şifreler eşleşmiyor.")
            ding_cal()
            seslendir("Şifreler eşleşmiyor")
            return

        try:
            bakiye = float(
                input("Başlangıç bakiyesi: ")
            )
        except ValueError:
            print("Geçerli bir sayı gir.")
            ding_cal()
            return

        basarili, mesaj = (
            self.veritabani.hesap_olustur(
                kullanici_adi,
                sifre,
                bakiye
            )
        )

        print(mesaj)

        if basarili:
            seslendir("Hesap başarıyla oluşturuldu")
        else:
            ding_cal()
            seslendir(mesaj)

    def giris_yap(self):
        print("\n========= BANKA GİRİŞİ =========")

        kullanici_adi = input(
            "Kullanıcı adı: "
        ).strip().lower()

        sifre = getpass.getpass(
            "Şifre: "
        )

        hesap = self.veritabani.giris_yap(
            kullanici_adi,
            sifre
        )

        if hesap is None:
            print("Kullanıcı adı veya şifre yanlış.")
            ding_cal()
            seslendir("Kullanıcı adı veya şifre yanlış")
            return False

        self.aktif_hesap_id = hesap[0]
        self.aktif_kullanici_adi = hesap[1]

        print(
            f"Giriş başarılı. Hoş geldin "
            f"{self.aktif_kullanici_adi}."
        )

        seslendir(
            f"Hoş geldin {self.aktif_kullanici_adi}"
        )

        return True

    def bakiye_goster(self):
        bakiye = self.veritabani.bakiye_getir(
            self.aktif_hesap_id
        )

        if bakiye is None:
            print("Hesap bulunamadı.")
            return

        print(f"Bakiyeniz: {bakiye:.2f} TL")
        seslendir(
            f"Bakiyeniz {bakiye:.0f} Türk lirası"
        )

    def para_yatir(self):
        try:
            miktar = float(
                input("Yatırılacak miktar: ")
            )
        except ValueError:
            print("Geçerli bir sayı gir.")
            ding_cal()
            return

        basarili, mesaj = self.veritabani.para_yatir(
            self.aktif_hesap_id,
            miktar
        )

        print(mesaj)

        if basarili:
            seslendir("Para yatırma işlemi başarılı")
            self.bakiye_goster()
        else:
            ding_cal()
            seslendir(mesaj)

    def para_cek(self):
        sifre = getpass.getpass(
            "Para çekmek için şifrenizi girin: "
        )

        hesap = self.veritabani.giris_yap(
            self.aktif_kullanici_adi,
            sifre
        )

        if hesap is None:
            print("Şifre yanlış.")
            ding_cal()
            seslendir("Şifre yanlış")
            return

        try:
            miktar = float(
                input("Çekilecek miktar: ")
            )
        except ValueError:
            print("Geçerli bir sayı gir.")
            ding_cal()
            return

        basarili, mesaj = self.veritabani.para_cek(
            self.aktif_hesap_id,
            miktar
        )

        print(mesaj)

        if basarili:
            seslendir("Para çekme işlemi başarılı")
            self.bakiye_goster()
        else:
            ding_cal()
            seslendir(mesaj)

    def transfer_yap(self):
        sifre = getpass.getpass(
            "Transfer için şifrenizi girin: "
        )

        hesap = self.veritabani.giris_yap(
            self.aktif_kullanici_adi,
            sifre
        )

        if hesap is None:
            print("Şifre yanlış.")
            ding_cal()
            seslendir("Şifre yanlış")
            return

        alici = input(
            "Alıcı kullanıcı adı: "
        ).strip().lower()

        try:
            miktar = float(
                input("Transfer miktarı: ")
            )
        except ValueError:
            print("Geçerli bir sayı gir.")
            ding_cal()
            return

        onay = input(
            f"{alici} hesabına {miktar:.2f} TL "
            f"gönderilsin mi? (e/h): "
        ).strip().lower()

        if onay != "e":
            print("Transfer iptal edildi.")
            seslendir("Transfer iptal edildi")
            return

        basarili, mesaj = (
            self.veritabani.para_transferi(
                self.aktif_hesap_id,
                alici,
                miktar
            )
        )

        print(mesaj)

        if basarili:
            seslendir("Para transferi başarılı")
            self.bakiye_goster()
        else:
            ding_cal()
            seslendir(mesaj)

    def islem_gecmisini_goster(self):
        islemler = (
            self.veritabani.islem_gecmisini_getir(
                self.aktif_hesap_id
            )
        )

        if not islemler:
            print("İşlem geçmişi bulunmuyor.")
            seslendir("İşlem geçmişi bulunmuyor")
            return

        print("\n========= İŞLEM GEÇMİŞİ =========")

        for sira, islem in enumerate(
            islemler,
            start=1
        ):
            islem_turu, miktar, aciklama, tarih = islem

            print(f"\n{sira}. işlem")
            print(f"Tür       : {islem_turu}")
            print(f"Miktar    : {miktar:.2f} TL")
            print(f"Açıklama  : {aciklama}")
            print(f"Tarih     : {tarih}")
            print("-" * 40)

    def sifre_degistir(self):
        eski_sifre = getpass.getpass(
            "Eski şifreniz: "
        )

        yeni_sifre = getpass.getpass(
            "Yeni şifreniz: "
        )

        tekrar = getpass.getpass(
            "Yeni şifreyi tekrar girin: "
        )

        if yeni_sifre != tekrar:
            print("Yeni şifreler eşleşmiyor.")
            ding_cal()
            seslendir("Şifreler eşleşmiyor")
            return

        basarili, mesaj = (
            self.veritabani.sifre_degistir(
                self.aktif_hesap_id,
                eski_sifre,
                yeni_sifre
            )
        )

        print(mesaj)

        if basarili:
            seslendir("Şifre başarıyla değiştirildi")
        else:
            ding_cal()
            seslendir(mesaj)

    def hesap_menusu(self):
        while True:
            print(
                f"""
========= SQL BANKA SİSTEMİ =========
Aktif kullanıcı: {self.aktif_kullanici_adi}

1- Bakiye Göster
2- Para Yatır
3- Para Çek
4- Para Transferi
5- İşlem Geçmişi
6- Şifre Değiştir
7- Oturumu Kapat
=======================================
"""
            )

            secim = input("Seçimin: ").strip()

            if secim == "1":
                self.bakiye_goster()

            elif secim == "2":
                self.para_yatir()

            elif secim == "3":
                self.para_cek()

            elif secim == "4":
                self.transfer_yap()

            elif secim == "5":
                self.islem_gecmisini_goster()

            elif secim == "6":
                self.sifre_degistir()

            elif secim == "7":
                print("Oturum kapatıldı.")
                seslendir("Oturum kapatıldı")

                self.aktif_hesap_id = None
                self.aktif_kullanici_adi = None
                break

            else:
                print("Geçersiz seçim.")
                ding_cal()
                seslendir("Geçersiz seçim")

    def ana_menu(self):
        seslendir("SQL banka sistemine hoş geldiniz")

        while True:
            print(
                """
========= PROJE 41 SQL BANKA =========
1- Sisteme Giriş Yap
2- Yeni Hesap Oluştur
3- Programı Kapat
========================================
"""
            )

            secim = input("Seçimin: ").strip()

            if secim == "1":
                if self.giris_yap():
                    self.hesap_menusu()

            elif secim == "2":
                self.yeni_hesap_olustur()

            elif secim == "3":
                print("Banka sistemi kapatılıyor.")
                seslendir("Görüşmek üzere Ertuğrul")
                break

            else:
                print("Geçersiz seçim.")
                ding_cal()
                seslendir("Geçersiz seçim")

        self.veritabani.kapat()


def main():
    uygulama = None

    try:
        uygulama = BankaUygulamasi()
        uygulama.ana_menu()

    except KeyboardInterrupt:
        print("\nProgram kullanıcı tarafından durduruldu.")

    except sqlite3.Error as hata:
        print(f"Veritabanı hatası: {hata}")
        ding_cal()
        seslendir("Veritabanı hatası oluştu")

    except Exception as hata:
        print(f"Beklenmeyen hata: {hata}")
        ding_cal()
        seslendir("Beklenmeyen bir hata oluştu")

    finally:
        if uygulama is not None:
            try:
                uygulama.veritabani.kapat()
            except sqlite3.Error:
                pass


if __name__ == "__main__":
    main()