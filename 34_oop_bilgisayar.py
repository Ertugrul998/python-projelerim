import subprocess


def seslendir(metin):
    subprocess.run(["say", metin], check=False)


class Bilgisayar:
    def __init__(self, marka, model, ram, ssd):
        self.marka = marka
        self.model = model
        self.ram = ram
        self.ssd = ssd

    def bilgileri_goster(self):
        print("\n--- BİLGİSAYAR ---")
        print(f"Marka: {self.marka}")
        print(f"Model: {self.model}")
        print(f"RAM: {self.ram} GB")
        print(f"SSD: {self.ssd} GB")

        seslendir(f"{self.marka} {self.model} bilgileri gösterildi")

    def ram_yukselt(self, miktar):
        self.ram += miktar
        print(f"Yeni RAM: {self.ram} GB")
        seslendir("RAM başarıyla yükseltildi")


pc = Bilgisayar(
    "Apple",
    "MacBook Pro M2",
    16,
    512
)

pc.bilgileri_goster()
pc.ram_yukselt(16)