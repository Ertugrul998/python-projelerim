import getpass
import subprocess
from datetime import datetime

DOGRU_SIFRE = "2580"
KALAN_HAK = 3
LOG_DOSYASI = "kasa_giris_kayitlari.txt"


def kayit_ekle(durum):
    tarih_saat = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    with open(LOG_DOSYASI, "a", encoding="utf-8") as dosya:
        dosya.write(f"{tarih_saat} - {durum}\n")


def kasa_acildi():
    print("✅ Şifre doğru.")
    print("🔓 Kasa açıldı.")

    subprocess.run([
        "say",
        "Kasa açıldı patron"
    ])

    kayit_ekle("Başarılı giriş")


def alarm_cal():

    subprocess.run([
        "osascript",
        "-e",
        "set volume output volume 100"
    ])

    print("🚨 Kasa kilitlendi!")

    kayit_ekle("Başarısız giriş nedeniyle kasa kilitlendi")

    subprocess.run([
        "osascript",
        "-e",
        'display notification "3 kez yanlış şifre girildi." '
        'with title "Kasa Güvenlik Uyarısı" sound name "Glass"'
    ])

    subprocess.run([
        "say",
        "Dikkat. Üç kez yanlış şifre girildi. Kasa kilitlendi."
    ])

    for tekrar in range(10):
        subprocess.run([
            "afplay",
            "-v",
            "2.0",
            "/System/Library/Sounds/Funk.aiff"
        ])


print("--- GELİŞMİŞ KASA GÜVENLİK SİSTEMİ ---")

kalan_hak = KALAN_HAK

while kalan_hak > 0:
    girilen_sifre = getpass.getpass("Kasa şifresini girin: ")

    if girilen_sifre == DOGRU_SIFRE:
        kasa_acildi()
        break

    kalan_hak -= 1

    print("❌ Şifre yanlış.")
    kayit_ekle("Başarısız şifre denemesi")

    if kalan_hak > 0:
        print("Kalan deneme hakkı:", kalan_hak)
    else:
        alarm_cal()