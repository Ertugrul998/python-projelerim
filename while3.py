import subprocess
import time

for i in range(10, 0, -1):
    subprocess.run([
    "osascript",
    "-e",
    f'display notification "{i}" with title "Ders çalışma zamanı" sound name "Glass"'

])
    print(i)
    time.sleep(1)

print("Bitti'")
