import getpass
import sqlite3
import subprocess
from datetime import datetime


SIFRE = "2580"
VERITABANI_ADI = "notlar.db"
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


def sifre_dogrula(mesaj="Şifreyi girin: "):
    girilen_sifre = getpass.getpass(mesaj)

    if girilen_sifre == SIFRE:
        print("Şifre doğru.")
        seslendir("Şifre doğru")
        return True

    print("Şifre yanlış!")
    ding_cal()
    seslendir("Şifre yanlış")
    return False


class NotVeritabani:
    def __init__(self):
        self.baglanti = sqlite3.connect(VERITABANI_ADI)
        self.imlec = self.baglanti.cursor()
        self.tablo_olustur()

    def tablo_olustur(self):
        self.imlec.execute(
            """
            CREATE TABLE IF NOT EXISTS notlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                baslik TEXT NOT NULL,
                icerik TEXT NOT NULL,
                tarih TEXT NOT NULL
            )
            """
        )

        self.baglanti.commit()

    def not_ekle(self):
        if not sifre_dogrula(
            "Not eklemek için şifreyi girin: "
        ):
            return

        baslik = input("Not başlığı: ").strip()
        icerik = input("Not içeriği: ").strip()

        if not baslik or not icerik:
            print("Başlık ve içerik boş bırakılamaz.")
            seslendir("Başlık ve içerik boş bırakılamaz")
            return

        tarih = datetime.now().strftime("%d.%m.%Y %H:%M")

        self.imlec.execute(
            """
            INSERT INTO notlar (baslik, icerik, tarih)
            VALUES (?, ?, ?)
            """,
            (baslik, icerik, tarih)
        )

        self.baglanti.commit()

        print("Not başarıyla kaydedildi.")
        seslendir("Not başarıyla kaydedildi")

    def notlari_yazdir(self, notlar):
        if not notlar:
            print("Kayıtlı not bulunamadı.")
            seslendir("Kayıtlı not bulunamadı")
            return

        print("\n========= KAYITLI NOTLAR =========")

        for not_id, baslik, icerik, tarih in notlar:
            print(f"\nID      : {not_id}")
            print(f"Başlık  : {baslik}")
            print(f"İçerik  : {icerik}")
            print(f"Tarih   : {tarih}")
            print("-" * 40)

    def notlari_listele(self):
        if not sifre_dogrula(
            "Notları görüntülemek için şifreyi girin: "
        ):
            return

        self.imlec.execute(
            """
            SELECT id, baslik, icerik, tarih
            FROM notlar
            ORDER BY id DESC
            """
        )

        notlar = self.imlec.fetchall()
        self.notlari_yazdir(notlar)

    def not_ara(self):
        if not sifre_dogrula(
            "Not aramak için şifreyi girin: "
        ):
            return

        kelime = input("Aranacak kelime: ").strip()

        if not kelime:
            print("Arama kelimesi boş bırakılamaz.")
            return

        self.imlec.execute(
            """
            SELECT id, baslik, icerik, tarih
            FROM notlar
            WHERE baslik LIKE ?
            OR icerik LIKE ?
            ORDER BY id DESC
            """,
            (f"%{kelime}%", f"%{kelime}%")
        )

        sonuclar = self.imlec.fetchall()

        if not sonuclar:
            print("Aramaya uygun not bulunamadı.")
            seslendir("Aramaya uygun not bulunamadı")
            return

        self.notlari_yazdir(sonuclar)

    def not_guncelle(self):
        if not sifre_dogrula(
            "Not güncellemek için şifreyi girin: "
        ):
            return

        self.imlec.execute(
            """
            SELECT id, baslik, icerik, tarih
            FROM notlar
            ORDER BY id
            """
        )

        notlar = self.imlec.fetchall()

        if not notlar:
            print("Güncellenecek not bulunmuyor.")
            return

        self.notlari_yazdir(notlar)

        try:
            not_id = int(
                input("Güncellenecek notun ID numarası: ")
            )
        except ValueError:
            print("Geçerli bir ID numarası girin.")
            ding_cal()
            return

        self.imlec.execute(
            """
            SELECT baslik, icerik
            FROM notlar
            WHERE id = ?
            """,
            (not_id,)
        )

        bulunan_not = self.imlec.fetchone()

        if bulunan_not is None:
            print("Bu ID numarasına ait not bulunamadı.")
            seslendir("Not bulunamadı")
            return

        eski_baslik, eski_icerik = bulunan_not

        yeni_baslik = input(
            f"Yeni başlık [{eski_baslik}]: "
        ).strip()

        yeni_icerik = input(
            f"Yeni içerik [{eski_icerik}]: "
        ).strip()

        if not yeni_baslik:
            yeni_baslik = eski_baslik

        if not yeni_icerik:
            yeni_icerik = eski_icerik

        yeni_tarih = datetime.now().strftime(
            "%d.%m.%Y %H:%M"
        )

        self.imlec.execute(
            """
            UPDATE notlar
            SET baslik = ?, icerik = ?, tarih = ?
            WHERE id = ?
            """,
            (
                yeni_baslik,
                yeni_icerik,
                yeni_tarih,
                not_id
            )
        )

        self.baglanti.commit()

        print("Not başarıyla güncellendi.")
        seslendir("Not başarıyla güncellendi")

    def not_sil(self):
        if not sifre_dogrula(
            "Not silmek için şifreyi girin: "
        ):
            return

        self.imlec.execute(
            """
            SELECT id, baslik, icerik, tarih
            FROM notlar
            ORDER BY id
            """
        )

        notlar = self.imlec.fetchall()

        if not notlar:
            print("Silinecek not bulunmuyor.")
            return

        self.notlari_yazdir(notlar)

        try:
            not_id = int(
                input("Silinecek notun ID numarası: ")
            )
        except ValueError:
            print("Geçerli bir ID numarası girin.")
            ding_cal()
            return

        self.imlec.execute(
            """
            SELECT baslik
            FROM notlar
            WHERE id = ?
            """,
            (not_id,)
        )

        bulunan_not = self.imlec.fetchone()

        if bulunan_not is None:
            print("Bu ID numarasına ait not bulunamadı.")
            seslendir("Not bulunamadı")
            return

        baslik = bulunan_not[0]

        onay = input(
            f"'{baslik}' başlıklı not silinsin mi? (e/h): "
        ).strip().lower()

        if onay != "e":
            print("Silme işlemi iptal edildi.")
            seslendir("Silme işlemi iptal edildi")
            return

        self.imlec.execute(
            """
            DELETE FROM notlar
            WHERE id = ?
            """,
            (not_id,)
        )

        self.baglanti.commit()

        print("Not başarıyla silindi.")
        seslendir("Not başarıyla silindi")

    def kapat(self):
        self.baglanti.close()


def menu():
    print("========= SQL NOT YÖNETİM SİSTEMİ =========")

    if not sifre_dogrula(
        "Sisteme giriş şifresini girin: "
    ):
        print("Giriş reddedildi. Sistem kapatılıyor.")
        seslendir("Giriş reddedildi. Sistem kapatılıyor")
        return

    veritabani = NotVeritabani()

    print("Giriş başarılı. Sistem açıldı.")
    seslendir("SQL not yönetim sistemine hoş geldiniz")

    while True:
        print(
            """
========= SQL NOT YÖNETİM SİSTEMİ =========
1- Not Ekle
2- Notları Listele
3- Not Ara
4- Not Güncelle
5- Not Sil
6- Çıkış
============================================
"""
        )

        secim = input("Seçimin: ").strip()

        if secim == "1":
            veritabani.not_ekle()

        elif secim == "2":
            veritabani.notlari_listele()

        elif secim == "3":
            veritabani.not_ara()

        elif secim == "4":
            veritabani.not_guncelle()

        elif secim == "5":
            veritabani.not_sil()

        elif secim == "6":
            veritabani.kapat()
            print("Veritabanı kapatıldı. Görüşmek üzere.")
            seslendir("Görüşmek üzere Ertuğrul")
            break

        else:
            print("Geçersiz seçim. 1 ile 6 arasında seçim yapın.")
            ding_cal()
            seslendir("Geçersiz seçim")


if __name__ == "__main__":
    menu()