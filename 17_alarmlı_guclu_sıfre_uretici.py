import random
import string
import subprocess
import threading


def sifre_uret(uzunluk):
    karakterler = (
        string.ascii_lowercase
        + string.ascii_uppercase
        + string.digits
        + string.punctuation
    )

    sifre = ""

    for tekrar in range(uzunluk):
        sifre += random.choice(karakterler)

    return sifre


def alarm_cal():
    # Mac sesini yüzde 100 yapar
    subprocess.run([
        "osascript",
        "-e",
        "set volume output volume 100"
    ])

    # Önce kadın konuşur
    subprocess.run([
        "say",
        "Dikkat. Geçersiz seçim yapıldı. Güvenlik alarmı aktif."
    ])

    alarm_durdur = threading.Event()
    aktif_alarm = {"islem": None}


    def alarm_sesi():
        while not alarm_durdur.is_set():

            aktif_alarm["islem"] = subprocess.Popen([
                "afplay",
                "-v",
                "5.0",
                "/System/Library/Sounds/Funk.aiff"
            ])

            aktif_alarm["islem"].wait()


    alarm_thread = threading.Thread(target=alarm_sesi)
    alarm_thread.start()

    input("\nAlarmı durdurmak için Enter tuşuna bas: ")

    alarm_durdur.set()

    if aktif_alarm["islem"] is not None:
        aktif_alarm["islem"].terminate()

    alarm_thread.join()

    print("🔕 Alarm durduruldu.")


while True:
    print("\n--- ALARMLI GÜÇLÜ ŞİFRE ÜRETİCİ ---")
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

                print("\n✅ Güçlü şifre oluşturuldu:")
                print(yeni_sifre)

                subprocess.run([
                    "say",
                    "Güçlü şifre oluşturuldu patron"
                ])

        except ValueError:
            print("❌ Lütfen yalnızca sayı girin.")

    elif secim == "2":
        print("Program kapatıldı.")
        break

    else:
        print("❌ Geçersiz seçim.")
        alarm_cal()