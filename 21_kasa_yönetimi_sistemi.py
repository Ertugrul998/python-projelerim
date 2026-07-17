import os

kasa = 1000
hata_sayisi = 0

while True:
    print("\n--- KASA YÖNETİM SİSTEMİ ---")
    print("1 - Para yatır")
    print("2 - Para çek")
    print("3 - Bakiye durumunu göster")
    print("4 - Çıkış")

    secim = input("Seçiminiz: ")

    if secim == "1":
        miktar = int(input("Yatırılacak miktar: "))
        kasa += miktar
        print("Para eklendi.")
        print("Yeni kasa:", kasa)

    elif secim == "2":
        miktar = int(input("Çekilecek miktar: "))

        if miktar <= kasa:
            kasa -= miktar
            print("Para çekildi.")
            print("Yeni kasa:", kasa)
        else:
            print("Yetersiz bakiye!")
            hata_sayisi += 1

            print("Hata sayısı:", hata_sayisi)

            os.system('afplay /System/Library/Sounds/Basso.aiff')
            os.system('say "Yetersiz bakiye"')

            if hata_sayisi == 3:
                print("🚨 Güvenlik alarmı aktif!")
                break

    elif secim == "3":
        print("Bakiyeyi göster:", kasa)

    elif secim == "4":
        print("Program kapatıldı.")
        break

    else:
        print("Geçersiz seçim!")



