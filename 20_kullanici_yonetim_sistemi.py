import os
# DİKKAT!
# Bu kod sonsuz alarm çalar.
# Durdurmak için Stop tuşuna bas.

dogru_kullanici = 'admin'
dogru_sifre = "2580"
hak = 3

while hak > 0:

    kullanici = input("Kullanıcı adı: ")
    sifre = input("Sifre: ")

    if kullanici == dogru_kullanici and sifre == dogru_sifre:
        print("Giriş başarılı!")
        break

    else:
        hak -= 1
        print("Hatalı giriş!")
        print("Kalan hak:", hak)

        if hak == 0:
            print("🚨 Hesap kilitlendi! 🚨")

            while True:
                os.system('afplay /System/Library/Sounds/Funk.aiff')
                os.system('say "Dikkat. Hesap kilitlendi!"')

