from datetime import datetime
import time
import os

gun = int(input("Gün: "))
ay = int(input("Ay: "))
yil = int(input("Yıl: "))
saat = int(input("Saat: "))
dakika = int(input("Dakika: "))

mesaj = input("Hatırlatma mesajı: ")

hedef_zaman = datetime(yil, ay, gun, saat, dakika)

if hedef_zaman <= datetime.now():
    print("Hata: Geçmiş bir tarih girdin.")
else:
    print("Hatırlatma kaydedildi.")
    print("Hedef zaman:", hedef_zaman.strftime("%d.%m.%Y %H:%M"))

    while datetime.now() < hedef_zaman:
        time.sleep(10)

    os.system(
        f'''osascript -e 'display notification "{mesaj}" with title "Hatırlatma"' '''
    )

    os.system(f'say "{mesaj}"')

    for i in range(5):
        os.system("afplay /System/Library/Sounds/Sosumi.aiff")