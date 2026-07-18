# Proje 25.1 - Sesli ve Alarmlı Gelişmiş Not Defteri
# İlk kullanımda kullanıcı kaydı oluşturur.
# Şifre küçük pencerede gizli olarak girilir.

import hashlib
import json
import os
import secrets
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import simpledialog


try:
    import speech_recognition as sr
    SES_TANIMA_VAR = True

except ModuleNotFoundError:
    SES_TANIMA_VAR = False


KULLANICI_DOSYASI = "not_defteri_kullanicisi.json"
NOT_DOSYASI = "notlar.txt"
ALARM_DOSYASI = "/System/Library/Sounds/Sosumi.aiff"


# -------------------------------------------------
# SESLİ KONUŞMA
# -------------------------------------------------

def sesli_konus(metin):
    try:
        subprocess.run(
            ["say", metin],
            check=False
        )

    except FileNotFoundError:
        pass


# -------------------------------------------------
# GİZLİ ŞİFRE GİRİŞİ
# -------------------------------------------------

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


# -------------------------------------------------
# ŞİFRELEME
# -------------------------------------------------

def sifre_ozeti_olustur(sifre, salt):
    veri = (salt + sifre).encode("utf-8")
    return hashlib.sha256(veri).hexdigest()


# -------------------------------------------------
# KULLANICI KAYDI
# -------------------------------------------------

def kullanici_kaydi_var_mi():
    return os.path.exists(KULLANICI_DOSYASI)


def ilk_kayit():
    print("\n====================================")
    print("         İLK KULLANICI KAYDI")
    print("====================================")

    sesli_konus("İlk kullanıcı kaydı oluşturuluyor.")

    while True:
        kullanici_adi = input(
            "Yeni kullanıcı adı: "
        ).strip()

        if not kullanici_adi:
            print("❌ Kullanıcı adı boş bırakılamaz.")
            sesli_konus("Kullanıcı adı boş bırakılamaz.")
            continue

        sifre = gizli_sifre_al(
            "Yeni kullanıcı kaydı",
            "Yeni şifrenizi giriniz:"
        )

        sifre_tekrar = gizli_sifre_al(
            "Şifre doğrulama",
            "Yeni şifrenizi tekrar giriniz:"
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
            print("❌ Girilen şifreler uyuşmuyor.")
            sesli_konus("Girilen şifreler uyuşmuyor.")
            continue

        salt = secrets.token_hex(16)

        sifre_ozeti = sifre_ozeti_olustur(
            sifre,
            salt
        )

        kullanici_bilgileri = {
            "kullanici_adi": kullanici_adi,
            "salt": salt,
            "sifre_ozeti": sifre_ozeti
        }

        with open(
            KULLANICI_DOSYASI,
            "w",
            encoding="utf-8"
        ) as dosya:

            json.dump(
                kullanici_bilgileri,
                dosya,
                ensure_ascii=False,
                indent=4
            )

        print("\n✅ Kullanıcı başarıyla oluşturuldu.")
        print("Şifreniz gizlenerek kaydedildi.")

        sesli_konus(
            "Kullanıcı başarıyla oluşturuldu."
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

    except FileNotFoundError:
        return None

    except json.JSONDecodeError:
        print("❌ Kullanıcı dosyası bozulmuş.")
        return None


# -------------------------------------------------
# ALARM VE SİSTEM KİLİDİ
# -------------------------------------------------

def alarm_sesi(durdurma_sinyali):
    while not durdurma_sinyali.is_set():
        subprocess.run(
            ["afplay", ALARM_DOSYASI],
            check=False
        )

        time.sleep(0.2)


def sistemi_kilitle():
    print("\n🚨 Üç kez hatalı giriş yapıldı!")
    print("🔒 Sistem kilitlendi.")
    print("⏎ Alarmı durdurmak için Enter tuşuna basınız.")

    sesli_konus(
        "Dikkat. Üç kez hatalı giriş yapıldı. "
        "Sistem kilitlendi. "
        "Alarmı durdurmak için Enter tuşuna basınız."
    )

    durdurma_sinyali = threading.Event()

    alarm_thread = threading.Thread(
        target=alarm_sesi,
        args=(durdurma_sinyali,),
        daemon=True
    )

    alarm_thread.start()

    input()

    durdurma_sinyali.set()
    alarm_thread.join(timeout=2)

    print("\n🔕 Alarm durduruldu.")
    print("Program kapatılıyor.")

    sesli_konus(
        "Alarm durduruldu. Program kapatılıyor."
    )

    sys.exit()


# -------------------------------------------------
# KULLANICI GİRİŞİ
# -------------------------------------------------

def giris_yap():
    kullanici_bilgileri = kullanici_bilgilerini_oku()

    if kullanici_bilgileri is None:
        print("❌ Kullanıcı bilgileri okunamadı.")
        sys.exit()

    hak = 3

    print("\n====================================")
    print("          NOT DEFTERİ GİRİŞİ")
    print("====================================")

    sesli_konus(
        "Gelişmiş not defterine giriş yapınız."
    )

    while hak > 0:
        kullanici_adi = input(
            "Kullanıcı adı: "
        ).strip()

        sifre = gizli_sifre_al(
            "Not Defteri Girişi",
            "Şifrenizi giriniz:"
        )

        girilen_sifre_ozeti = sifre_ozeti_olustur(
            sifre,
            kullanici_bilgileri["salt"]
        )

        kullanici_dogru = (
            kullanici_adi
            == kullanici_bilgileri["kullanici_adi"]
        )

        sifre_dogru = (
            girilen_sifre_ozeti
            == kullanici_bilgileri["sifre_ozeti"]
        )

        if kullanici_dogru and sifre_dogru:
            print("\n✅ Giriş başarılı.")
            print("Hoş geldiniz,", kullanici_adi)

            sesli_konus(
                f"Giriş başarılı. Hoş geldiniz {kullanici_adi}."
            )

            return

        hak -= 1

        print("\n❌ Kullanıcı adı veya şifre hatalı.")
        print("Kalan giriş hakkı:", hak)

        if hak > 0:
            sesli_konus(
                f"Hatalı giriş. Kalan giriş hakkınız {hak}."
            )

    sistemi_kilitle()


# -------------------------------------------------
# NOT DOSYASI İŞLEMLERİ
# -------------------------------------------------

def notlari_oku():
    try:
        with open(
            NOT_DOSYASI,
            "r",
            encoding="utf-8"
        ) as dosya:

            return [
                satir.strip()
                for satir in dosya
                if satir.strip()
            ]

    except FileNotFoundError:
        return []


def notlari_kaydet(notlar):
    with open(
        NOT_DOSYASI,
        "w",
        encoding="utf-8"
    ) as dosya:

        for not_metni in notlar:
            dosya.write(not_metni + "\n")


def notu_dosyaya_ekle(not_metni):
    with open(
        NOT_DOSYASI,
        "a",
        encoding="utf-8"
    ) as dosya:

        dosya.write(not_metni + "\n")


# -------------------------------------------------
# KLAVYEYLE NOT EKLEME
# -------------------------------------------------

def klavyeyle_not_ekle():
    print("\n===== KLAVYEYLE NOT EKLE =====")

    sesli_konus(
        "Eklemek istediğiniz notu klavyeden yazınız."
    )

    not_metni = input(
        "Notunuzu yazınız: "
    ).strip()

    if not not_metni:
        print("❌ Boş not eklenemez.")
        sesli_konus("Boş not eklenemez.")
        return

    notu_dosyaya_ekle(not_metni)

    print("✅ Not başarıyla kaydedildi.")
    sesli_konus("Not başarıyla kaydedildi.")


# -------------------------------------------------
# SESLİ KOMUT ÇALIŞMAZSA
# -------------------------------------------------

def klavyeye_yonlendir():
    mesaj = (
        "Sesli komutunuz bulunmamaktadır, "
        "klavyeden yazınız."
    )

    print("\n⚠️", mesaj)
    sesli_konus(mesaj)

    klavyeyle_not_ekle()


# -------------------------------------------------
# MİKROFONLA NOT EKLEME
# -------------------------------------------------

def mikrofonla_not_ekle():
    if not SES_TANIMA_VAR:
        klavyeye_yonlendir()
        return

    taniyici = sr.Recognizer()

    print("\n===== MİKROFONLA NOT EKLE =====")
    print("🎤 Notunuzu söyleyin...")

    sesli_konus("Notunuzu söyleyin.")

    try:
        with sr.Microphone() as kaynak:
            taniyici.adjust_for_ambient_noise(
                kaynak,
                duration=1
            )

            ses = taniyici.listen(
                kaynak,
                timeout=8,
                phrase_time_limit=30
            )

        print("Ses yazıya dönüştürülüyor...")

        not_metni = taniyici.recognize_google(
            ses,
            language="tr-TR"
        )

        print("Algılanan not:", not_metni)

        sesli_konus(
            "Söylediğiniz not algılandı."
        )

        onay = input(
            "Bu not kaydedilsin mi? (e/h): "
        ).strip().lower()

        if onay != "e":
            print("Not kaydedilmedi.")
            sesli_konus("Not kaydedilmedi.")
            return

        notu_dosyaya_ekle(not_metni)

        print("✅ Sesli not başarıyla kaydedildi.")
        sesli_konus(
            "Sesli not başarıyla kaydedildi."
        )

    except sr.WaitTimeoutError:
        print("❌ Belirlenen sürede konuşma algılanmadı.")
        klavyeye_yonlendir()

    except sr.UnknownValueError:
        print("❌ Söylediğiniz not anlaşılamadı.")
        klavyeye_yonlendir()

    except sr.RequestError:
        print("❌ Ses tanıma hizmetine ulaşılamadı.")
        klavyeye_yonlendir()

    except (OSError, AttributeError):
        print("❌ Mikrofon veya sesli komut açılamadı.")
        klavyeye_yonlendir()


# -------------------------------------------------
# NOTLARI GÖSTERME
# -------------------------------------------------

def notlari_goster():
    notlar = notlari_oku()

    if not notlar:
        print("\n📭 Kayıtlı not bulunamadı.")
        sesli_konus("Kayıtlı not bulunamadı.")
        return

    print("\n===== KAYITLI NOTLAR =====")

    for sira, not_metni in enumerate(
        notlar,
        start=1
    ):
        print(f"{sira} - {not_metni}")

    sesli_konus(
        f"Toplam {len(notlar)} not bulundu."
    )


# -------------------------------------------------
# NOT SİLME
# -------------------------------------------------

def not_sil():
    notlar = notlari_oku()

    if not notlar:
        print("\n📭 Silinecek not bulunamadı.")
        sesli_konus("Silinecek not bulunamadı.")
        return

    print("\n===== KAYITLI NOTLAR =====")

    for sira, not_metni in enumerate(
        notlar,
        start=1
    ):
        print(f"{sira} - {not_metni}")

    try:
        secim = int(
            input(
                "Silmek istediğiniz notun numarası: "
            )
        )

        if secim < 1 or secim > len(notlar):
            print("❌ Geçersiz not numarası.")
            sesli_konus("Geçersiz not numarası.")
            return

        silinen_not = notlar.pop(secim - 1)
        notlari_kaydet(notlar)

        print("🗑️ Silinen not:", silinen_not)
        sesli_konus("Not başarıyla silindi.")

    except ValueError:
        print("❌ Lütfen yalnızca sayı giriniz.")
        sesli_konus("Lütfen yalnızca sayı giriniz.")


# -------------------------------------------------
# BÜTÜN NOTLARI SİLME
# -------------------------------------------------

def tum_notlari_sil():
    notlar = notlari_oku()

    if not notlar:
        print("\n📭 Silinecek not bulunamadı.")
        sesli_konus("Silinecek not bulunamadı.")
        return

    onay = input(
        "Tüm notlar silinsin mi? (e/h): "
    ).strip().lower()

    if onay == "e":
        notlari_kaydet([])

        print("🗑️ Tüm notlar silindi.")
        sesli_konus("Tüm notlar silindi.")

    else:
        print("İşlem iptal edildi.")
        sesli_konus("İşlem iptal edildi.")


# -------------------------------------------------
# ANA MENÜ
# -------------------------------------------------

def ana_menu():
    while True:
        print("\n====================================")
        print("       GELİŞMİŞ NOT DEFTERİ")
        print("====================================")
        print("1 - Klavyeyle not ekle")
        print("2 - Mikrofonla sesli not ekle")
        print("3 - Notları göster")
        print("4 - Not sil")
        print("5 - Tüm notları sil")
        print("6 - Çıkış")

        sesli_konus(
            "Hangi işlemi yapmak istiyorsunuz?"
        )

        secim = input(
            "Seçiminiz: "
        ).strip()

        if secim == "1":
            klavyeyle_not_ekle()

        elif secim == "2":
            mikrofonla_not_ekle()

        elif secim == "3":
            notlari_goster()

        elif secim == "4":
            not_sil()

        elif secim == "5":
            tum_notlari_sil()

        elif secim == "6":
            print("\nProgram kapatılıyor...")
            sesli_konus("Program kapatılıyor.")
            break

        else:
            print("\n❌ Geçersiz seçim yaptınız.")
            sesli_konus("Geçersiz seçim yaptınız.")


# -------------------------------------------------
# PROGRAMI BAŞLAT
# -------------------------------------------------

if not kullanici_kaydi_var_mi():
    ilk_kayit()

giris_yap()
ana_menu()