import subprocess
baslik = "Merhaba"
mesaj = "Bu bir deneme mesajıdır."

komut = f'display notification "{mesaj}" with title "{baslik} sound name "Glass"'

subprocess.run(["osascript", "-e", komut])
