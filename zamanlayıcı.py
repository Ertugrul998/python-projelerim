import subprocess
import time
print("1 dakika mola başladı...")

dakika = int(input("Kaç dakika mola vereceksin? "))

print(f"{dakika} dakikalık mola başladı...")

time.sleep(60)     #60 saniye = 1 dakika

subprocess.run([
    "osascript",
    "-e",
    'display notification "Molan bitti! Derse dön." with title "Python Hatırlatıcısı" sound name "Sosumi"'

])

print ("Alarm durdurmak için Enter tuşuna bas.")

import threading
alarm_dursun = False

def alarm_call():
    while not alarm_dursun:
        subprocess.run([
            "afplay",
            "/System/Library/Sounds/Sosumi.aiff"
        ])

thread =threading.Thread(target=alarm_call)
thread.start()
input("Alarm durdurmak için Enter tuşuna bas...")

alarm_dursun = True
thread.join()

print("Alarm durduruldu.")