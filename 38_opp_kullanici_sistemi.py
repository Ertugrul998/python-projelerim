import getpass
import subprocess


SIFRE = "2580"
DING_SESI = "/System/Library/Sounds/Glass.aiff"


def seslendir(metin):
    subprocess.run(["say", metin], check=False)


def ding_cal():
    subprocess.run(
        ["afplay", DING_SESI],
        check=False
    )


class Kullanici:
    def __init__(self, kullanici_adi, sifre):
        self.kullanici_adi = kullanici_adi
        self.sifre = sifre

    def giris_yap(self):
        girilen_sifre = getpass.getpass("Şifreyi gir: ")

        if girilen_sifre == self.sifre:
            print("Giriş başarılı.")
            seslendir("Giriş başarılı")
            return True

        print("Şifre yanlış!")
        ding_cal()
        seslendir("Şifre yanlış. Sistem kapatılıyor")
        return False

    def bilgileri_goster(self):
        print("\n--- KULLANICI BİLGİLERİ ---")
        print(f"Kullanıcı adı: {self.kullanici_adi}")
        seslendir("Kullanıcı bilgileri gösterildi")

    def sifre_degistir(self):
        eski_sifre = getpass.getpass("Eski şifreyi gir: ")

        if eski_sifre != self.sifre:
            print("Eski şifre yanlış!")
            ding_cal()
            seslendir("Eski şifre yanlış")
            return

        yeni_sifre = getpass.getpass("Yeni şifreyi gir: ")
        tekrar = getpass.getpass("Yeni şifreyi tekrar gir: ")

        if yeni_sifre != tekrar:
            print("Yeni şifreler eşleşmiyor.")
            ding_cal()
            seslendir("Yeni şifreler eşleşmiyor")
            return

        if not yeni_sifre:
            print("Şifre boş bırakılamaz.")
            return

        self.sifre = yeni_sifre
        print("Şifre başarıyla değiştirildi.")
        seslendir("Şifre başarıyla değiştirildi")


def menu():
    kullanici = Kullanici(
        kullanici_adi="Ertuğrul",
        sifre=SIFRE
    )

    print("========= OOP KULLANICI SİSTEMİ =========")

    if not kullanici.giris_yap():
        print("Sistem kapatıldı.")
        return

    while True:
        print("""
========= KULLANICI MENÜSÜ =========
1- Kullanıcı Bilgilerini Göster
2- Şifre Değiştir
3- Çıkış
=====================================
""")

        secim = input("Seçimin: ").strip()

        if secim == "1":
            kullanici.bilgileri_goster()

        elif secim == "2":
            kullanici.sifre_degistir()

        elif secim == "3":
            print("Sistem kapatılıyor.")
            seslendir("Görüşmek üzere Ertuğrul")
            break

        else:
            print("Geçersiz seçim.")
            ding_cal()
            seslendir("Geçersiz seçim")


if __name__ == "__main__":
    menu()