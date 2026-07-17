import os
import time

bakiye = 1000
dogru_pin = "2580"

kart_takili = False
giris_yapildi = False
pin_hata = 0

while True:
    print("\n--- DİJİTAL ATM ---")
    print("1 - Kart tak")
    print("2 - Para çek")
    print("3 - Para yatır")
    print("4 - Bakiye göster")
    print("5 - Kart çıkar")
    print("6 - Çıkış")

    secim = input("Seçiminiz: ")

    if secim == "1":

        if kart_takili:
            print("Kart zaten takılı!")

        else:
            kart_takili = True
            print("💳 Kart takıldı.")

        while pin_hata < 3:
            pin = input("PIN giriniz: ")

            if pin == dogru_pin:
                giris_yapildi = True
                print("✅ Giriş işlemi başarılı.")
                break

            else:
                pin_hata += 1
                print("❌ Hatalı PIN!")
                print("Kalan hakkınız:",3 - pin_hata)

                os.system('afplay /System/Library/Sounds/Basso.aiff')
                os.system('say "Hatali PIN"')

            if pin_hata >= 3:
                print("🚨 Güvenik alarmı aktif!")
                print("💳 Kartınız bloke olmuştur!")
                print("💳 Kart ATM tarafından yutulmuştur!")
                print("📞 Lütfen banka ile iletişime geçiniz.")

                time.sleep(5)

                raise SystemExit

