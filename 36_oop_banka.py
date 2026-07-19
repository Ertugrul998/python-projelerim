import getpass
import subprocess


SIFRE = "2580"
ALARM_SESI = "/System/Library/Sounds/Sosumi.aiff"


def seslendir(metin):
    subprocess.run(["say", metin], check=False)


def alarm_cal():
    seslendir("Dikkat! Hatalı şifre girildi")

    subprocess.run(
        ["afplay", ALARM_SESI],
        check=False
    )


class BankaHesabi:
    def __init__(self, hesap_sahibi, bakiye, sifre):
        self.hesap_sahibi = hesap_sahibi
        self.bakiye = bakiye
        self.sifre = sifre

    def sifre_kontrol(self, mesaj="Şifrenizi girin: "):
        girilen = getpass.getpass(mesaj)

        if girilen == self.sifre:
            print("Şifre doğru.")
            seslendir("Şifre doğru")
            return True

        print("Şifre yanlış!")
        alarm_cal()
        return False

    def bakiye_goster(self):
        if not self.sifre_kontrol(
            "Bakiyeyi görmek için şifrenizi girin: "
        ):
            return

        print(f"Bakiyeniz: {self.bakiye:.2f} TL")
        seslendir(
            f"Bakiyeniz {self.bakiye:.0f} Türk lirası"
        )

    def para_yatir(self, miktar):
        if miktar <= 0:
            print("Geçersiz miktar.")
            seslendir("Geçersiz miktar")
            return

        self.bakiye += miktar

        print(f"{miktar:.2f} TL yatırıldı.")
        print(f"Yeni bakiye: {self.bakiye:.2f} TL")

        seslendir("Para yatırma işlemi başarılı")

    def para_cek(self, miktar):
        if not self.sifre_kontrol(
            "Para çekmek için şifrenizi girin: "
        ):
            return

        if miktar <= 0:
            print("Geçersiz miktar.")
            seslendir("Geçersiz miktar")
            return

        if miktar > self.bakiye:
            print("Yetersiz bakiye!")
            seslendir("Yetersiz bakiye")
            return

        self.bakiye -= miktar

        print(f"{miktar:.2f} TL çekildi.")
        print(f"Kalan bakiye: {self.bakiye:.2f} TL")

        seslendir("Para çekme işlemi başarılı")


def sisteme_giris_yap():
    girilen = getpass.getpass(
        "Banka sistemi giriş şifresi: "
    )

    if girilen == SIFRE:
        print("Giriş başarılı.")
        seslendir("Giriş başarılı")
        return True

    print("Şifre yanlış!")
    alarm_cal()
    return False


def menu():
    if not sisteme_giris_yap():
        print("Sisteme giriş reddedildi.")
        seslendir("Sisteme giriş reddedildi")
        return

    hesap = BankaHesabi(
        hesap_sahibi="Ertuğrul",
        bakiye=10000,
        sifre=SIFRE
    )

    seslendir("O O P banka sistemine hoş geldiniz")

    while True:
        print("""
========= OOP BANKA SİSTEMİ =========
1- Bakiye Göster
2- Para Yatır
3- Para Çek
4- Hesap Bilgileri
5- Çıkış
======================================
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
            print("\n--- HESAP BİLGİLERİ ---")
            print(f"Hesap sahibi: {hesap.hesap_sahibi}")
            print(f"Bakiye: {hesap.bakiye:.2f} TL")

            seslendir("Hesap bilgileri gösterildi")

        elif secim == "5":
            print("Banka sistemi kapatılıyor.")
            seslendir("Görüşmek üzere Ertuğrul")
            break

        else:
            print("Geçersiz seçim.")
            seslendir("Geçersiz seçim")


if __name__ == "__main__":
    menu()