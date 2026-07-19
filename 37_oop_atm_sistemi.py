import getpass
import subprocess
from datetime import datetime


ALARM_SESI = "/System/Library/Sounds/Sosumi.aiff"


def seslendir(metin):
    subprocess.run(["say", metin], check=False)


def alarm_cal():
    seslendir("Dikkat! Kart bloke edildi")

    subprocess.run(
        ["afplay", ALARM_SESI],
        check=False
    )


class BankaHesabi:
    def __init__(self, hesap_sahibi, kart_no, pin, bakiye):
        self.hesap_sahibi = hesap_sahibi
        self.kart_no = kart_no
        self.pin = pin
        self.bakiye = bakiye
        self.bloke = False
        self.islem_gecmisi = []

    def islem_kaydet(self, aciklama):
        tarih = datetime.now().strftime("%d.%m.%Y %H:%M")
        self.islem_gecmisi.append(
            f"{tarih} - {aciklama}"
        )

    def kart_dogrula(self):
        girilen_kart = input("Kart numarası: ").strip()

        if girilen_kart == self.kart_no:
            print("Kart doğrulandı.")
            return True

        print("Kart numarası yanlış.")
        seslendir("Kart numarası yanlış")
        return False

    def pin_dogrula(self):
        if self.bloke:
            print("Kartınız bloke edilmiştir.")
            seslendir("Kartınız bloke edilmiştir")
            return False

        for deneme in range(1, 4):
            girilen_pin = getpass.getpass("PIN girin: ")

            if girilen_pin == self.pin:
                print("Giriş başarılı.")
                seslendir("Giriş başarılı")
                self.islem_kaydet("Başarılı giriş")
                return True

            kalan_hak = 3 - deneme

            print("PIN yanlış!")
            seslendir("PIN yanlış")

            self.islem_kaydet(
                f"Başarısız PIN denemesi: {deneme}"
            )

            if kalan_hak > 0:
                print(f"Kalan deneme hakkı: {kalan_hak}")

        self.bloke = True

        print("Kartınız bloke edildi.")
        self.islem_kaydet("Kart bloke edildi")
        alarm_cal()

        return False

    def bakiye_goster(self):
        print(f"Bakiyeniz: {self.bakiye:.2f} TL")
        seslendir(
            f"Bakiyeniz {self.bakiye:.0f} Türk lirası"
        )

        self.islem_kaydet("Bakiye görüntülendi")

    def para_yatir(self, miktar):
        if miktar <= 0:
            print("Geçersiz miktar.")
            seslendir("Geçersiz miktar")
            return

        self.bakiye += miktar

        print(f"{miktar:.2f} TL yatırıldı.")
        print(f"Yeni bakiye: {self.bakiye:.2f} TL")

        seslendir("Para yatırma işlemi başarılı")

        self.islem_kaydet(
            f"{miktar:.2f} TL yatırıldı"
        )

    def para_cek(self, miktar):
        if miktar <= 0:
            print("Geçersiz miktar.")
            seslendir("Geçersiz miktar")
            return

        if miktar > self.bakiye:
            print("Yetersiz bakiye!")
            seslendir("Yetersiz bakiye")

            self.islem_kaydet(
                f"Başarısız para çekme: {miktar:.2f} TL"
            )
            return

        self.bakiye -= miktar

        print(f"{miktar:.2f} TL çekildi.")
        print(f"Kalan bakiye: {self.bakiye:.2f} TL")

        seslendir("Para çekme işlemi başarılı")

        self.islem_kaydet(
            f"{miktar:.2f} TL çekildi"
        )

    def gecmisi_goster(self):
        if not self.islem_gecmisi:
            print("İşlem geçmişi bulunmuyor.")
            return

        print("\n========= İŞLEM GEÇMİŞİ =========")

        for sira, kayit in enumerate(
            self.islem_gecmisi,
            start=1
        ):
            print(f"{sira}- {kayit}")


def atm_menu(hesap):
    while True:
        print("""
========= OOP ATM SİSTEMİ =========
1- Bakiye Göster
2- Para Yatır
3- Para Çek
4- İşlem Geçmişi
5- Kartı Çıkar
====================================
""")

        secim = input("Seçimin: ").strip()

        if secim == "1":
            hesap.bakiye_goster()

        elif secim == "2":
            try:
                miktar = float(
                    input("Yatırılacak miktar: ")
                )
                hesap.para_yatir(miktar)

            except ValueError:
                print("Geçerli bir sayı gir.")
                seslendir("Geçerli bir sayı gir")

        elif secim == "3":
            try:
                miktar = float(
                    input("Çekilecek miktar: ")
                )
                hesap.para_cek(miktar)

            except ValueError:
                print("Geçerli bir sayı gir.")
                seslendir("Geçerli bir sayı gir")

        elif secim == "4":
            hesap.gecmisi_goster()

        elif secim == "5":
            print("Kartınız çıkarılıyor.")
            seslendir("Kartınızı almayı unutmayınız")
            break

        else:
            print("Geçersiz seçim.")
            seslendir("Geçersiz seçim")


def main():
    hesap = BankaHesabi(
        hesap_sahibi="Ertuğrul",
        kart_no="1234567890123456",
        pin="2580",
        bakiye=15000
    )

    print("========= ATM'YE HOŞ GELDİNİZ =========")
    seslendir("ATM sistemine hoş geldiniz")

    if not hesap.kart_dogrula():
        print("İşlem sonlandırıldı.")
        return

    if not hesap.pin_dogrula():
        print("ATM işlemi sonlandırıldı.")
        return

    atm_menu(hesap)


if __name__ == "__main__":
    main()