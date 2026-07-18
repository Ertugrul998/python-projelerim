# Proje 27 - Sesli ve Şifreli Günlük
# Sürüm 1.0

import datetime
import hashlib
import json
import os
import secrets
import subprocess
import sys
import tkinter as tk
from tkinter import simpledialog


KULLANICI_DOSYASI = "gunluk_kullanicisi.json"
GUNLUK_DOSYASI = "gunluk.txt"


def sesli_konus(metin):
    subprocess.run(
        ["say", metin],
        check=False
    )


def gizli_sifre_al(baslik, mesaj):
    pencere = tk.Tk()
    pencere.withdraw()
    pencere.attributes("-topmost", True)

    sifre = simpledialog.askstring(
        baslik,
        mesaj,
        show="*",
        parent=pencere
    )

    pencere.destroy()

    if sifre is None:
        return ""

    return sifre


def sifre_ozeti_olustur(sifre, salt):
    veri = (salt + sifre).encode("utf-8")
    return hashlib.sha256(veri).hexdigest()


def kullanici_kaydi_var_mi():
    return os.path.exists(KULLANICI_DOSYASI)


def kullanici_olustur():
    print("\n================================")
    print("       İLK KULLANICI KAYDI")
    print("================================")

    sesli_konus("İlk günlük kullanıcısı oluşturuluyor.")

    while True:
        kullanici_adi = input(
            "Yeni kullanıcı adı: "
        ).strip()

        if not kullanici_adi:
            print("❌ Kullanıcı adı boş bırakılamaz.")
            sesli_konus("Kullanıcı adı boş bırakılamaz.")
            continue

        sifre = gizli_sifre_al(
            "Günlük Kaydı",
            "Yeni şifrenizi giriniz:"
        )

        sifre_tekrar = gizli_sifre_al(
            "Şifre Doğrulama",
            "Şifrenizi tekrar giriniz:"
        )

        if not sifre:
            print("❌ Şifre boş bırakılamaz.")
            sesli_konus("Şifre boş bırakılamaz.")
            continue

        if len(sifre) < 4:
            print("❌ Şifre en az 4 karakter olmalıdır.")
            sesli_konus(
                "Şifre en az dört karakter olmalıdır."
            )
            continue

        if sifre != sifre_tekrar:
            print("❌ Şifreler uyuşmuyor.")
            sesli_konus("Şifreler uyuşmuyor.")
            continue

        salt = secrets.token_hex(16)

        bilgiler = {
            "kullanici_adi": kullanici_adi,
            "salt": salt,
            "sifre_ozeti": sifre_ozeti_olustur(
                sifre,
                salt
            )
        }

        with open(
            KULLANICI_DOSYASI,
            "w",
            encoding="utf-8"
        ) as dosya:
            json.dump(
                bilgiler,
                dosya,
                ensure_ascii=False,
                indent=4
            )

        print("✅ Günlük kullanıcısı oluşturuldu.")
        sesli_konus(
            "Günlük kullanıcısı başarıyla oluşturuldu."
        )
        return


def kullanici_bilgilerini_oku():
    try:
        with open(
            KULLANICI_DOSYASI,
            "r",
            encoding="utf-8"
        ) as dosya:
            return json.load(dosya)

    except (FileNotFoundError, json.JSONDecodeError):
        return None


def giris_yap():
    bilgiler = kullanici_bilgilerini_oku()

    if bilgiler is None:
        print("❌ Kullanıcı bilgileri okunamadı.")
        sesli_konus("Kullanıcı bilgileri okunamadı.")
        sys.exit()

    hak = 3

    print("\n================================")
    print("         GÜNLÜK GİRİŞİ")
    print("================================")

    sesli_konus("Şifreli günlüğe giriş yapınız.")

    while hak > 0:
        kullanici_adi = input(
            "Kullanıcı adı: "
        ).strip()

        sifre = gizli_sifre_al(
            "Günlük Girişi",
            "Şifrenizi giriniz:"
        )

        girilen_ozet = sifre_ozeti_olustur(
            sifre,
            bilgiler["salt"]
        )

        kullanici_dogru = (
            kullanici_adi == bilgiler["kullanici_adi"]
        )

        sifre_dogru = (
            girilen_ozet == bilgiler["sifre_ozeti"]
        )

        if kullanici_dogru and sifre_dogru:
            print("✅ Giriş başarılı.")
            sesli_konus("Giriş başarılı. Hoş geldiniz.")
            return True

        hak -= 1

        print("❌ Kullanıcı adı veya şifre hatalı.")
        print("Kalan giriş hakkı:", hak)

        if hak > 0:
            sesli_konus(
                f"Hatalı giriş. Kalan hakkınız {hak}."
            )

    print("\n🔒 Günlük kilitlendi.")
    sesli_konus(
        "Üç kez hatalı giriş yapıldı. Günlük kilitlendi."
    )

    return False


def gunluk_yaz():
    print("\n===== GÜNLÜK YAZ =====")

    sesli_konus("Bugünkü günlüğünüzü yazınız.")

    metin = input(
        "Günlük yazınız: "
    ).strip()

    if not metin:
        print("❌ Boş günlük kaydedilemez.")
        sesli_konus("Boş günlük kaydedilemez.")
        return

    tarih = datetime.datetime.now().strftime(
        "%d.%m.%Y %H:%M"
    )

    with open(
        GUNLUK_DOSYASI,
        "a",
        encoding="utf-8"
    ) as dosya:
        dosya.write(f"\n[{tarih}]\n")
        dosya.write(metin + "\n")

    print("✅ Günlük başarıyla kaydedildi.")
    sesli_konus("Günlük başarıyla kaydedildi.")


def gunlugu_oku():
    try:
        with open(
            GUNLUK_DOSYASI,
            "r",
            encoding="utf-8"
        ) as dosya:
            icerik = dosya.read()

        if not icerik.strip():
            print("📭 Günlük kaydı bulunamadı.")
            sesli_konus("Günlük kaydı bulunamadı.")
            return

        print("\n===== GÜNLÜK KAYITLARI =====")
        print(icerik)

        sesli_konus("Günlük kayıtları gösterildi.")

    except FileNotFoundError:
        print("📭 Henüz günlük kaydı bulunmuyor.")
        sesli_konus("Henüz günlük kaydı bulunmuyor.")


def tum_gunlugu_sil():
    if not os.path.exists(GUNLUK_DOSYASI):
        print("📭 Silinecek günlük kaydı bulunamadı.")
        sesli_konus(
            "Silinecek günlük kaydı bulunamadı."
        )
        return

    onay = input(
        "Tüm günlük kayıtları silinsin mi? (e/h): "
    ).strip().lower()

    if onay == "e":
        with open(
            GUNLUK_DOSYASI,
            "w",
            encoding="utf-8"
        ):
            pass

        print("🗑️ Tüm günlük kayıtları silindi.")
        sesli_konus(
            "Tüm günlük kayıtları silindi."
        )

    else:
        print("İşlem iptal edildi.")
        sesli_konus("İşlem iptal edildi.")


def ana_menu():
    while True:
        print("\n================================")
        print("          ŞİFRELİ GÜNLÜK")
        print("================================")
        print("1 - Günlük yaz")
        print("2 - Günlüğü oku")
        print("3 - Tüm günlüğü sil")
        print("4 - Çıkış")

        sesli_konus("Hangi işlemi yapmak istiyorsunuz?")

        secim = input("Seçiminiz: ").strip()

        if secim == "1":
            gunluk_yaz()

        elif secim == "2":
            gunlugu_oku()

        elif secim == "3":
            tum_gunlugu_sil()

        elif secim == "4":
            print("\n✅ Çıkış yapıldı.")
            sesli_konus("Çıkış yapıldı.")
            break

        else:
            print("\n❌ Hatalı giriş yaptınız.")
            sesli_konus("Hatalı giriş yaptınız.")


if not kullanici_kaydi_var_mi():
    kullanici_olustur()

if giris_yap():
    ana_menu()