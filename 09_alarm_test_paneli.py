import sys
import subprocess
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout
)


def alarmi_test_et():
    subprocess.run([
        "afplay",
        "/System/Library/Sounds/Sosumi.aiff"
    ])

    subprocess.run([
        "osascript",
        "-e",
        'display notification "Alarm sistemi başarıyla çalışıyor." '
        'with title "Alarm Testi"'
    ])
    subprocess.run([
        "say",
        "Patron alarm sistemi başarıyla çalışıyor"
    ])

app = QApplication(sys.argv)

pencere = QWidget()
pencere.setWindowTitle("Python Alarm Uygulaması")
pencere.resize(450, 300)

simdi = datetime.now()

yazi = QLabel(f"""
🐍 Python Hazır ✅
💻 PyCharm Hazır ✅

📅 Tarih: {simdi.strftime('%d.%m.%Y')}
🕒 Saat: {simdi.strftime('%H:%M:%S')}
""")

yazi.setStyleSheet("""
    font-size: 18px;
    padding: 20px;
""")

buton = QPushButton("🔊 Alarmı Test Et")
buton.setStyleSheet("""
    font-size: 17px;
    padding: 12px;
""")

buton.clicked.connect(alarmi_test_et)

duzen = QVBoxLayout()
duzen.addWidget(yazi)
duzen.addWidget(buton)

pencere.setLayout(duzen)
pencere.show()

sys.exit(app.exec())
