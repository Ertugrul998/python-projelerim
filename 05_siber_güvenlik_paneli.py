from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from datetime import datetime
import sys
import os

# Mac konuşsun
os.system("say 'Hoş geldin Ertuğrul'")

app = QApplication(sys.argv)

pencere = QWidget()
pencere.setWindowTitle("🛡️ Siber Güvenlik Merkezi")
pencere.resize(600, 300)

simdi = datetime.now()

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

yazi.setStyleSheet("""
font-size: 18px;
padding: 20px;
""")

duzen = QVBoxLayout()
duzen.addWidget(yazi)

pencere.setLayout(duzen)
pencere.show()

sys.exit(app.exec())
