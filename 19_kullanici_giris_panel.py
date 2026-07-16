import subprocess
import threading
from datetime import datetime


DOGRU_KULLANICI = "Ertugrul"
DOGRU_SIFRE = "2580"
DENEME_HAKKI = 3

KAYIT_DOSYASI = "kullanici_giris_kayitlari.txt"


def giris_kaydet(durum):
    tarih = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    with open(KAYIT_DOSYASI, "a", encoding="utf-8") as dosya:
        dosya.write(f"{tarih} -> {durum}\n")


def alarm_sesi(alarm_durdur):
    while not alarm_durdur.is_set():
        ses = subprocess.Popen([
            "afplay",
            "-v",
            "5.0",
            "/System/Library/Sounds/Funk.aiff"
        ])

        while ses.poll() is None:
            if alarm_durdur.is_set():
                ses.terminate()
                break


def alarm_cal():
    subprocess.run([
        "osascript",
        "-e",
        "set volume output volume 100"
    ])

    subprocess.run([
        "say",
        "Dikkat. Yetkisiz giriş denemesi algılandı."
    ])

    alarm_durdur = threading.Event()

    alarm_thread = threading.Thread(
        target=alarm_sesi,
        args=(alarm_durdur,)
    )

    alarm_thread.start()

    input("Alarmı durdurmak için Enter tuşuna bas: ")

    alarm_durdur.set()
    subprocess.run(["pkill", "-f", "afplay"])
    alarm_thread.join()

    print("🔕 Alarm durduruldu.")


kalan_hak = DENEME_HAKKI

print("\n--- KULLANICI GİRİŞ PANELİ ---")

while kalan_hak > 0:
    kullanici_adi = input("Kullanıcı adı: ")
    sifre = input("Şifre: ")

    if kullanici_adi == DOGRU_KULLANICI and sifre == DOGRU_SIFRE:
        print("✅ Giriş başarılı.")
        giris_kaydet("Başarılı giriş")
        break

    else:
        kalan_hak -= 1

        print("❌ Hatalı kullanıcı adı veya şifre.")
        print("Kalan hak:", kalan_hak)

        giris_kaydet("Başarısız giriş")

        if kalan_hak == 0:
            print("🚨 Alarm aktif!")
            alarm_cal()