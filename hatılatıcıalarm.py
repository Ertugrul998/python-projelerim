import threading
import time
import os

mesaj = input("Hatırlatma: ")
dakika = int(input("Kaç dakika sonra: "))

time.sleep(dakika * 60)

os.system(f'''osascript -e 'display notification "{mesaj}" with title "Hatırlatma"' ''')
os.system(f'say "{mesaj}"')

for i in range(5):
    os.system("afplay /System/Library/Sounds/Sosumi.aiff")