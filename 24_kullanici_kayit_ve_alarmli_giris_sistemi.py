# Proje 24 - Kullanıcı Kayıt ve Giriş Sistemi
# Sürüm 2.0

import os
import subprocess
import sys
import threading
import time


KULLANICI_DOSYASI = "kullanicilar.txt"


def sesli_konus(metin):
    subprocess.run(
        ["say", metin],
        check=False
    )


def alarm_sesi(durdurma_sinyali):
    alarm_dosyasi = "/System/Library/Sounds/Sosumi.aiff"

    while not durdurma_sinyali.is_set():
        subprocess.run(
            ["afplay", alarm_dosyasi],
            check=False
        )
        time.sleep(0.2)


def alarm_ve_kilitle():
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
    alarm_thread.join(timeout=1)

    sesli_konus("Alarm durduruldu. Program kapatılıyor.")
    print("🔕 Alarm durduruldu.")
    print("Program kapatılıyor.")

    sys.exit()


def dosyayi_hazirla():
    if not os.path.exists(KULLANICI_DOSYASI):
        with open(KULLANICI_DOSYASI, "w", encoding="utf-8"):
            pass


def kullanici_var_mi(kullanici_adi):
    with open(KULLANICI_DOSYASI, "r", encoding="utf-8") as dosya:
        for satir in dosya:
            satir = satir.strip()

            if not satir:
                continue

            parcalar = satir.split(",", 1)

            if len(parcalar) != 2:
                continue

            kayitli_ad, _ = parcalar

            if kullanici_adi == kayitli_ad:
                return True

    return False


def kayit_ol():
    print("\n--- KAYIT OL ---")

    kullanici_adi = input("Kullanıcı adı giriniz: ").strip()
    sifre = input("Şifre giriniz: ").strip()

    if not kullanici_adi or not sifre:
        print("❌ Kullanıcı adı ve şifre boş bırakılamaz.")
        return

    if kullanici_var_mi(kullanici_adi):
        print("⚠️ Bu kullanıcı adı zaten kayıtlı.")
        return

    with open(KULLANICI_DOSYASI, "a", encoding="utf-8") as dosya:
        dosya.write(f"{kullanici_adi},{sifre}\n")

    print("✅ Kullanıcı kaydedildi.")
    sesli_konus("Kullanıcı başarıyla kaydedildi.")


def bilgiler_dogru_mu(giris_adi, giris_sifre):
    with open(KULLANICI_DOSYASI, "r", encoding="utf-8") as dosya:
        for satir in dosya:
            satir = satir.strip()

            if not satir:
                continue

            parcalar = satir.split(",", 1)

            if len(parcalar) != 2:
                continue

            kayitli_ad, kayitli_sifre = parcalar

            if giris_adi == kayitli_ad and giris_sifre == kayitli_sifre:
                return True

    return False


def giris_yap():
    hak = 3

    print("\n--- GİRİŞ YAP ---")

    while hak > 0:
        giris_adi = input("Kullanıcı adı: ").strip()
        giris_sifre = input("Şifre: ").strip()

        if bilgiler_dogru_mu(giris_adi, giris_sifre):
            print("\n✅ Giriş başarılı.")
            print("--- KULLANICI PANELİ ---")
            print("Hoş geldiniz,", giris_adi)
            print("Sistem kullanıma hazır.")

            sesli_konus(
                f"Giriş başarılı. Hoş geldiniz {giris_adi}."
            )
            return

        hak -= 1

        print("\n❌ Kullanıcı adı veya şifre hatalı.")
        print("Kalan giriş hakkı:", hak)

        if hak > 0:
            sesli_konus(
                f"Hatalı giriş. Kalan giriş hakkınız {hak}."
            )

    alarm_ve_kilitle()


def ana_menu():
    dosyayi_hazirla()

    while True:
        print("\n==============================")
        print(" KULLANICI YÖNETİM SİSTEMİ")
        print("==============================")
        print("1 - Kayıt ol")
        print("2 - Giriş yap")
        print("3 - Çıkış")

        secim = input("Seçiminiz: ").strip()

        if secim == "1":
            kayit_ol()

        elif secim == "2":
            giris_yap()

        elif secim == "3":
            print("Program kapatılıyor.")
            sesli_konus("Program kapatılıyor.")
            break

        else:
            print("❌ Geçersiz seçim.")


ana_menu()
