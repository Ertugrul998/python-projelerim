import threading
import random
import string
import subprocess
from datetime import datetime

KAYIT_DOSYASI = "profesyonel_sifre_kayitlari.txt"

def sifre_kaydet(sifre):
    tarih = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    with open(KAYIT_DOSYASI, "a", encoding="utf-8") as dosya:
        dosya.write(f"{tarih} -> {sifre}\n")

def sifre_uret(sifre_uzunlugu):
    karakterler = (
        string.ascii_lowercase
        + string.ascii_uppercase
        + string.digits
        + string.punctuation
    )

    sifre = ""

    for tekrar in range(sifre_uzunlugu):
        sifre += random.choice(karakterler)

    return sifre

def alarm_sesli(alarm_durdur: threading.Event):
    while not alarm_durdur.is_set():
        alarm_process = subprocess.Popen([
            "afplay",
            "-v",
            "5.0",
            "/System/Library/Sounds/Funk.aiff"
        ])

        alarm_process.wait()

def alarm_cal():
    subprocess.run([
        "osascript",
        "-e",
        "set volume output volume 100"
    ])

    subprocess.run([
        "say",
        "Dikkat. Geçersiz seçim yapıldı. Güvenlik alarmı aktif."
    ])

    alarm_durdur = threading.Event()

    alarm_thread = threading.Thread(
        target=alarm_sesli,
        args=(alarm_durdur,)
    )

    alarm_thread.start()

    input("Alarmı durdurmak için Enter tuşuna bas: ")

    alarm_durdur.set()
    subprocess.run(["pkill", "-f", "afplay"])
    alarm_thread.join()

    print("🔕 Alarm durduruldu.")

while True:
    print("\n--- PROFESYONEL ŞİFRE ÜRETİCİ ---")
    print("1 - Şifre üret")
    print("2 - Çıkış")

    secim = input("Seçiminiz: ")

    if secim == "1":
        try:
            uzunluk = int(input("Şifre kaç karakter olsun?: "))

            if uzunluk < 8:
                print("❌ Şifre en az 8 karakter olmalı.")

            else:

                yeni_sifre = sifre_uret(uzunluk)

                print("✅ Şifreniz:", yeni_sifre)

                sifre_kaydet(yeni_sifre)

                print("💾 Şifre dosyaya kaydedildi.")

        except ValueError:

            print("❌ Lütfen yalnızca sayı girin.")

    elif secim == "2":

        print("Program kapatıldı.")

        break

    else:

        print("❌ Geçersiz seçim.")
        alarm_cal()

