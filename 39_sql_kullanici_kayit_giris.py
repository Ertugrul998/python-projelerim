import getpass
import hashlib
import sqlite3
import subprocess
from pathlib import Path


VERITABANI = Path("kullanicilar.db")
DING_SESI = "/System/Library/Sounds/Glass.aiff"


def seslendir(metin):
    subprocess.run(
        ["say", metin],
        check=False
    )


def ding_cal():
    subprocess.run(
        ["afplay", DING_SESI],
        check=False
    )


def sifreyi_hashle(sifre):
    return hashlib.sha256(
        sifre.encode("utf-8")
    ).hexdigest()


class KullaniciVeritabani:
    def __init__(self, dosya_adi):
        self.baglanti = sqlite3.connect(dosya_adi)
        self.imlec = self.baglanti.cursor()
        self.tabloyu_olustur()

    def tabloyu_olustur(self):
        self.imlec.execute(
            """
            CREATE TABLE IF NOT EXISTS kullanicilar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_adi TEXT UNIQUE NOT NULL,
                sifre TEXT NOT NULL
            )
            """
        )

        self.baglanti.commit()

    def kullanici_kaydet(self, kullanici_adi, sifre):
        if not kullanici_adi or not sifre:
            print("Kullanıcı adı ve şifre boş bırakılamaz.")
            seslendir("Bilgiler boş bırakılamaz")
            return

        sifre_hash = sifreyi_hashle(sifre)

        try:
            self.imlec.execute(
                """
                INSERT INTO kullanicilar
                (kullanici_adi, sifre)
                VALUES (?, ?)
                """,
                (kullanici_adi, sifre_hash)
            )

            self.baglanti.commit()

            print("Kullanıcı başarıyla kaydedildi.")
            seslendir("Kullanıcı başarıyla kaydedildi")

        except sqlite3.IntegrityError:
            print("Bu kullanıcı adı zaten kayıtlı.")
            ding_cal()
            seslendir("Bu kullanıcı adı zaten kayıtlı")

    def giris_yap(self, kullanici_adi, sifre):
        sifre_hash = sifreyi_hashle(sifre)

        self.imlec.execute(
            """
            SELECT id, kullanici_adi
            FROM kullanicilar
            WHERE kullanici_adi = ?
            AND sifre = ?
            """,
            (kullanici_adi, sifre_hash)
        )

        kullanici = self.imlec.fetchone()

        if kullanici is not None:
            print(f"Giriş başarılı. Hoş geldin {kullanici[1]}.")
            seslendir(f"Hoş geldin {kullanici[1]}")
            return True

        print("Kullanıcı adı veya şifre yanlış!")
        ding_cal()
        seslendir("Kullanıcı adı veya şifre yanlış")
        return False

    def kullanicilari_listele(self):
        self.imlec.execute(
            """
            SELECT id, kullanici_adi
            FROM kullanicilar
            ORDER BY id
            """
        )

        kullanicilar = self.imlec.fetchall()

        if not kullanicilar:
            print("Kayıtlı kullanıcı bulunmuyor.")
            return

        print("\n========= KAYITLI KULLANICILAR =========")

        for kullanici_id, kullanici_adi in kullanicilar:
            print(
                f"ID: {kullanici_id} | "
                f"Kullanıcı adı: {kullanici_adi}"
            )

    def kullanici_sil(self, kullanici_adi, sifre):
        sifre_hash = sifreyi_hashle(sifre)

        self.imlec.execute(
            """
            DELETE FROM kullanicilar
            WHERE kullanici_adi = ?
            AND sifre = ?
            """,
            (kullanici_adi, sifre_hash)
        )

        self.baglanti.commit()

        if self.imlec.rowcount > 0:
            print("Kullanıcı başarıyla silindi.")
            seslendir("Kullanıcı başarıyla silindi")
        else:
            print("Kullanıcı adı veya şifre yanlış.")
            ding_cal()
            seslendir("Kullanıcı silinemedi")

    def kapat(self):
        self.baglanti.close()


def menu():
    veritabani = KullaniciVeritabani(VERITABANI)

    seslendir("SQL kullanıcı sistemine hoş geldiniz")

    while True:
        print(
            """
========= SQL KULLANICI SİSTEMİ =========
1- Yeni Kullanıcı Kaydet
2- Giriş Yap
3- Kullanıcıları Listele
4- Kullanıcı Sil
5- Çıkış
==========================================
"""
        )

        secim = input("Seçimin: ").strip()

        if secim == "1":
            kullanici_adi = input(
                "Yeni kullanıcı adı: "
            ).strip()

            sifre = getpass.getpass(
                "Yeni şifre: "
            )

            sifre_tekrar = getpass.getpass(
                "Şifreyi tekrar gir: "
            )

            if sifre != sifre_tekrar:
                print("Şifreler eşleşmiyor!")
                ding_cal()
                seslendir("Şifreler eşleşmiyor")
                continue

            veritabani.kullanici_kaydet(
                kullanici_adi,
                sifre
            )

        elif secim == "2":
            kullanici_adi = input(
                "Kullanıcı adı: "
            ).strip()

            sifre = getpass.getpass(
                "Şifre: "
            )

            veritabani.giris_yap(
                kullanici_adi,
                sifre
            )

        elif secim == "3":
            veritabani.kullanicilari_listele()

        elif secim == "4":
            kullanici_adi = input(
                "Silinecek kullanıcı adı: "
            ).strip()

            sifre = getpass.getpass(
                "Kullanıcının şifresi: "
            )

            onay = input(
                f"'{kullanici_adi}' silinsin mi? (e/h): "
            ).strip().lower()

            if onay == "e":
                veritabani.kullanici_sil(
                    kullanici_adi,
                    sifre
                )
            else:
                print("Silme işlemi iptal edildi.")

        elif secim == "5":
            veritabani.kapat()

            print("SQL kullanıcı sistemi kapatılıyor.")
            seslendir("Görüşmek üzere Ertuğrul")
            break

        else:
            print("Geçersiz seçim.")
            ding_cal()
            seslendir("Geçersiz seçim")


if __name__ == "__main__":
    menu()
