import random
import string
import subprocess


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


while True:
    print("\n--- GÜÇLÜ ŞİFRE ÜRETİCİ ---")
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