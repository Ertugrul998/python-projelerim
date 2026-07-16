import sys
import subprocess

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout
)

kalan_saniye = 10


def ekrani_guncelle():
    dakika = kalan_saniye // 60
    saniye = kalan_saniye % 60
    sayac_yazisi.setText(f"{dakika:02d}:{saniye:02d}")


def sayaci_baslat():
    global kalan_saniye

    if kalan_saniye <= 0:
        kalan_saniye = 10
        ekrani_guncelle()

    zamanlayici.start(1000)
    durum_yazisi.setText("🟢 Çalışma başladı")


def sayaci_durdur():
    zamanlayici.stop()
    durum_yazisi.setText("⏸️ Sayaç durduruldu")


def sayaci_sifirla():
    global kalan_saniye

    zamanlayici.stop()
    kalan_saniye = 10
    ekrani_guncelle()
    durum_yazisi.setText("🔄 Sayaç sıfırlandı")

def geri_say():
    global kalan_saniye

    if kalan_saniye > 0:
        kalan_saniye -= 1
        ekrani_guncelle()
    else:
        zamanlayici.stop()
        durum_yazisi.setText("☕ Mola zamanı!")
        subprocess.Popen([
            "curl",
            "-X",
            "POST",
            "https://api.pushcut.io/kuxe7lvRVZXSoTZVkAUuP/execute?shortcut=Metni%20Seslendir"
        ])

        subprocess.Popen([
            "say",
            "Patron. Çalışma süresi tamamlandı. Mola zamanı."
        ])


app = QApplication(sys.argv)

pencere = QWidget()
pencere.setWindowTitle("🛡️ SİBER GÜVENLİK ÇALIŞMA MERKEZİ")
pencere.resize(500, 420)

baslik = QLabel("🛡️ SİBER GÜVENLİK ÇALIŞMA MERKEZİ")
baslik.setStyleSheet("""
font-size: 21px;
font-weight: bold;
padding: 10px;
""")

sayac_yazisi = QLabel("25:00")
sayac_yazisi.setStyleSheet("""
font-size: 65px;
font-weight: bold;
padding: 25px;
""")

durum_yazisi = QLabel("⚪ Başlamaya hazır")
durum_yazisi.setStyleSheet("""
font-size: 17px;
padding: 10px;
""")

baslat_butonu = QPushButton("▶️ Başlat")
durdur_butonu = QPushButton("⏸️ Durdur")
sifirla_butonu = QPushButton("🔄 Sıfırla")

baslat_butonu.clicked.connect(sayaci_baslat)
durdur_butonu.clicked.connect(sayaci_durdur)
sifirla_butonu.clicked.connect(sayaci_sifirla)

buton_stili = """
font-size: 16px;
padding: 10px;
"""

baslat_butonu.setStyleSheet(buton_stili)
durdur_butonu.setStyleSheet(buton_stili)
sifirla_butonu.setStyleSheet(buton_stili)

zamanlayici = QTimer()
zamanlayici.timeout.connect(geri_say)

duzen = QVBoxLayout()
duzen.addWidget(baslik)
duzen.addWidget(sayac_yazisi)
duzen.addWidget(durum_yazisi)
duzen.addWidget(baslat_butonu)
duzen.addWidget(durdur_butonu)
duzen.addWidget(sifirla_butonu)

pencere.setLayout(duzen)

pencere.setStyleSheet("""
QWidget {
    background-color: #1e1e1e;
    color: white;
}

QPushButton {
    background-color: #2d2d2d;
    border: 1px solid #555;
    border-radius: 8px;
    padding: 8px;
}

QPushButton:hover {
    background-color: #3d3d3d;
}
""")

pencere.show()

subprocess.Popen([
    "say",
    "Patron. Pomodoro sistemi hazır."
])

sys.exit(app.exec())
