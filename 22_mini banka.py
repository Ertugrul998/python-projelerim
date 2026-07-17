import os

kasa = 1000
hata_sayisi = 0

while True:
    print("\n--- KASA YÖNETİM SİSTEMİ ---")
    print("1 - Para ekle")
    print("2 - Para çek")
    print("3 - Kasa durumunu göster")
    print("4 - Çıkış")

    secim = input("Seçiminiz: ")

    if secim == "1":
        miktar = int(input("Eklenecek miktar: "))
        kasa += miktar
        print("Para eklendi.")
        print("Yeni kasa:", kasa)

    elif secim == "2":
        miktar = int(input("Eklenecek miktar: "))

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
                print("🚨 Güvenik alarmı aktif!")
                print("💳 Kartınız bloke olmuştur!")
                print("📞 Lütfen banka ile iletişime geçiniz.")

                os.system("osascript -e 'set volume output volume 100'")
                os.system('say -v Yelda  "Dikkat. Güvenlik alarmı aktif."')

                alarm_sayisi = 0

                while alarm_sayisi < 10:
                    os.system('afplay /System/Library/Sounds/Hero.aiff')
                    alarm_sayisi += 1

                break

    elif secim == "3":
        print("Kasadaki para:", kasa)

    elif secim == "4":
        print("Program kapatıldı.")
        break

    else:
        print("Geçersiz seçim!")



