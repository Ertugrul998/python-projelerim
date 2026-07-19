import subprocess


def seslendir(metin):
    subprocess.run(["say", metin], check=False)


class Arac:
    def __init__(self, marka, model, kilometre):
        self.marka = marka
        self.model = model
        self.kilometre = kilometre

    def calistir(self):
        print(f"{self.marka} {self.model} çalıştırıldı.")
        seslendir("Araç çalıştırıldı")

    def kilometre_ekle(self, miktar):
        self.kilometre += miktar
        print(f"Yeni kilometre: {self.kilometre}")
        seslendir("Kilometre bilgisi güncellendi")

    def bilgileri_goster(self):
        print("\n--- ARAÇ BİLGİLERİ ---")
        print(f"Marka: {self.marka}")
        print(f"Model: {self.model}")
        print(f"Kilometre: {self.kilometre}")


aracim = Arac(
    "Mercedes",
    "Maybach",
    25000
)

aracim.calistir()
aracim.kilometre_ekle(150)
aracim.bilgileri_goster()