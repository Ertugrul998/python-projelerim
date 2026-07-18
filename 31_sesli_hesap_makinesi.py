import subprocess


sesli_mod = False


def sesli_konus(metin):
    if sesli_mod:
        subprocess.run(
            ["say", metin],
            check=False
        )


def mod_sec():
    global sesli_mod

    while True:
        print("\n=== SES MODU ===")
        print("1 - Sesli")
        print("2 - Sessiz")

        secim = input("Seçiminiz: ").strip()

        if secim == "1":
            sesli_mod = True
            print("🔊 Sesli mod açıldı.")
            sesli_konus("Sesli mod açıldı.")
            return

        elif secim == "2":
            sesli_mod = False
            print("🔇 Sessiz mod açıldı.")
            return

        else:
            print("❌ Hatalı giriş yaptınız.")


def ana_menu():
    while True:
        print("\n========================")
        print("      HESAP MAKİNESİ")
        print("========================")
        print("1 - Toplama")
        print("2 - Çıkarma")
        print("3 - Çarpma")
        print("4 - Bölme")
        print("5 - Üs alma")
        print("6 - Çıkış")

        sesli_konus("Bir işlem seçiniz.")

        secim = input("Seçiminiz: ").strip()

        if secim == "6":
            print("👋 Çıkış yapıldı.")
            sesli_konus("Çıkış yapıldı.")
            break

        if secim not in ["1", "2", "3", "4", "5"]:
            print("❌ Hatalı giriş yaptınız.")
            sesli_konus("Hatalı giriş yaptınız.")
            continue

        try:
            sayi1 = float(input("1. sayı: "))
            sayi2 = float(input("2. sayı: "))

        except ValueError:
            print("❌ Lütfen geçerli bir sayı giriniz.")
            sesli_konus("Lütfen geçerli bir sayı giriniz.")
            continue

        if secim == "1":
            sonuc = sayi1 + sayi2

        elif secim == "2":
            sonuc = sayi1 - sayi2

        elif secim == "3":
            sonuc = sayi1 * sayi2

        elif secim == "4":
            if sayi2 == 0:
                print("❌ Sıfıra bölünemez.")
                sesli_konus("Sıfıra bölünemez.")
                continue

            sonuc = sayi1 / sayi2

        else:
            sonuc = sayi1 ** sayi2

        print(f"\n✅ Sonuç: {sonuc}")
        sesli_konus(f"Sonuç {sonuc}")


mod_sec()
ana_menu()