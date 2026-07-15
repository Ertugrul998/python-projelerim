from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton
from datetime import datetime
import sys
import subprocess
from datetime import datetime

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout

# Mac konuşsun
subprocess.run([
    "say",
    "Patron Ertuğrul. Siber Güvenlik Merkezi aktif edildi. Tüm sistemler hazır'"
 ])

app = QApplication(sys.argv)

pencere = QWidget()
pencere.setWindowTitle("🛡️ Siber Güvenlik Merkezi")
pencere.resize(600, 300)

simdi = datetime.now()

def alarmi_test_et():
    subprocess.Popen([
        "say",
        "Patron. Alarm testi başarılı. Sistem sorunsuz çalışıyor."
    ])

yazi = QLabel(f"""
🛡️ SİBER GÜVENLİK MERKEZİ

👋 Hoş geldin Ertuğrul!

👀 Seni göremeyeceğimi mi sandın?
🧿 Benim 2 gözüm var. Seni görüyorum. 😎

🐍 Python Hazır      ✅
💻 PyCharm Hazır     ✅

📅 Tarih: {simdi.strftime('%d.%m.%Y')}
🕒 Saat : {simdi.strftime('%H:%M:%S')}
""")
buton = QPushButton("🔊 Alarmı Test Et")

buton.clicked.connect(alarmi_test_et)

duzen = QVBoxLayout()

duzen.addWidget(yazi)
duzen.addWidget(buton)

pencere.setLayout(duzen)

yazi.setStyleSheet("""
font-size: 18px;
padding: 20px;
""")

pencere.show()

sys.exit(app.exec())
