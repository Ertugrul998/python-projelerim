import os
import time
import subprocess

def hatirlatici_ekle():

    mesaj = input("Hatırlatma mesajı: ")
    saniye = int(input("Kaç saniye sonra hatırlatsın?: "))

    print("\nHatırlatıcı kuruldu...")

    time.sleep(saniye)

    print("\n🔔 ALARM 🔔")
    print("Hatırlatma:", mesaj)

    #Alarm sesi
    subprocess.run([
        "afplay",
        "/System/Library/Sounds/Glass.aiff"
    ])

    #Mesaj sesli okuma
    subprocess.run([
        "say",
        mesaj
    ])

    # Bildirim gönderir
    subprocess.run([
        "osascript",
        "-e",
        f'display notification "{mesaj}" with title "Hatırlatıcı" sound name "Glass"'
    ])

while True:

    print("\n---MENÜ ---")
    print("1 - Hatırlatıcı Ekle")
    print("2 - Çıkış")

    secim = input("Seçiminiz: ")

    if secim == "1":
        hatirlatici_ekle()

    elif secim == "2":
        print("Program kapatıldı.")
        break

    else:
        print("Geçersiz seçim!")
