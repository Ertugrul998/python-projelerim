import os
import subprocess
from datetime import datetime

DOGRU_SIFRE = "2580"
DENEME_HAKKI = 3

KORUNAN_DOSYA = "gizli_notlar.txt"
KAYIT_DOSYASI = "dosya_guvenlik_kayitlari.txt"


def kayit_ekle(durum):
    tarih_saat = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    with open(KAYIT_DOSYASI, "a", encoding="utf-8") as dosya:
        dosya.write(f"{tarih_saat} - {durum}\n")


def dosya_olustur():
    if not os.path.exists(KORUNAN_DOSYA):
        with open(KORUNAN_DOSYA, "w", encoding="utf-8") as dosya:
            dosya.write("Bu dosya şifre ile korunmaktadır.\n")
            dosya.write("Gizli not: Python çalışmaya devam et!\n")


def dosyayi_goster():
    print("\n🔓 Erişim izni verildi.")
    print("--- KORUNAN DOSYA ---")

    with open(KORUNAN_DOSYA, "r", encoding="utf-8") as dosya:
        print(dosya.read())

    subprocess.run([
        "say",
        "Erişim izni verildi patron"
    ])

    kayit_ekle("Başarılı dosya erişimi")


def alarm_cal():
    print("\n🚨 YETKİSİZ ERİŞİM!")
    print("🔒 Dosya kilitlendi.")

    kayit_ekle("Üç yanlış şifre nedeniyle erişim engellendi")

    # Mac sesini yüzde 100 yapar
    subprocess.run([
        "osascript",
        "-e",
        "set volume output volume 100"
    ])

    # Bildirim gönderir
    subprocess.run([
        "osascript",
        "-e",
        'display notification "3 kez yanlış şifre girildi." '
        'with title "Dosya Güvenlik Alarmı" sound name "Glass"'
    ])

    # Sesli uyarı
    subprocess.run([
        "say",
        "Dikkat. Yetkisiz dosya erişimi tespit edildi. Sistem kilitlendi."
    ])

    # Alarmı 10 kez çalar
    for tekrar in range(10):
        subprocess.run([
            "afplay",
            "-v",
            "5.0",
            "/System/Library/Sounds/Funk.aiff"
        ])


dosya_olustur()

print("--- DOSYA KORUMA SİSTEMİ ---")

kalan_hak = DENEME_HAKKI

while kalan_hak > 0:
    girilen_sifre = input("Dosya şifresini girin: ")

    if girilen_sifre == DOGRU_SIFRE:
        dosyayi_goster()
        break

    kalan_hak -= 1
    print("❌ Şifre yanlış.")

    kayit_ekle("Başarısız şifre denemesi")

    if kalan_hak > 0:
        print("Kalan deneme hakkı:", kalan_hak)
    else:
        alarm_cal()
