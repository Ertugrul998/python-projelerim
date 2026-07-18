# Proje 25.0 - Gelişmiş Not Defteri
# Sesli ve alarmsız sürüm

import subprocess
import sys


KULLANICI_ADI = "Ertugrul"
SIFRE = "1234"
NOT_DOSYASI = "notlar.txt"


def sesli_konus(metin):
    subprocess.run(
        ["say", metin],
        check=False
    )


def giris_yap():
    hak = 3

    print("\n===== NOT DEFTERİ GİRİŞİ =====")
    sesli_konus("Gelişmiş not defterine giriş yapınız.")

    while hak > 0:
        kullanici_adi = input("Kullanıcı adı: ").strip()
        sifre = input("Şifre: ").strip()

        if kullanici_adi == KULLANICI_ADI and sifre == SIFRE:
            print("\n✅ Giriş başarılı.")
            sesli_konus("Giriş başarılı. Hoş geldiniz.")
            return

        hak -= 1

        print("\n❌ Kullanıcı adı veya şifre hatalı.")
        print("Kalan giriş hakkı:", hak)

        if hak > 0:
            sesli_konus(
                f"Hatalı giriş. Kalan giriş hakkınız {hak}."
            )

    print("\n🔒 Hesap kilitlendi.")
    print("Program kapatılıyor.")

    sesli_konus(
        "Üç kez hatalı giriş yapıldı. "
        "Hesap kilitlendi. Program kapatılıyor."
    )

    sys.exit()


def notlari_oku():
    try:
        with open(NOT_DOSYASI, "r", encoding="utf-8") as dosya:
            return [
                satir.strip()
                for satir in dosya
                if satir.strip()
            ]

    except FileNotFoundError:
        return []


def notlari_kaydet(notlar):
    with open(NOT_DOSYASI, "w", encoding="utf-8") as dosya:
        for not_metni in notlar:
            dosya.write(not_metni + "\n")


def not_ekle():
    print("\n===== NOT EKLE =====")
    sesli_konus("Eklemek istediğiniz notu yazınız.")

    not_metni = input("Notunuzu yazınız: ").strip()

    if not not_metni:
        print("❌ Boş not eklenemez.")
        sesli_konus("Boş not eklenemez.")
        return

    with open(NOT_DOSYASI, "a", encoding="utf-8") as dosya:
        dosya.write(not_metni + "\n")

    print("✅ Not başarıyla kaydedildi.")
    sesli_konus("Not başarıyla kaydedildi.")


def notlari_goster():
    notlar = notlari_oku()

    if not notlar:
        print("\n📭 Kayıtlı not bulunamadı.")
        sesli_konus("Kayıtlı not bulunamadı.")
        return

    print("\n===== KAYITLI NOTLAR =====")

    for sira, not_metni in enumerate(notlar, start=1):
        print(f"{sira} - {not_metni}")

    sesli_konus(
        f"Toplam {len(notlar)} not bulundu."
    )


def not_sil():
    notlar = notlari_oku()

    if not notlar:
        print("\n📭 Silinecek not bulunamadı.")
        sesli_konus("Silinecek not bulunamadı.")
        return

    print("\n===== KAYITLI NOTLAR =====")

    for sira, not_metni in enumerate(notlar, start=1):
        print(f"{sira} - {not_metni}")

    try:
        secim = int(
            input("Silmek istediğiniz notun numarasını giriniz: ")
        )

        if secim < 1 or secim > len(notlar):
            print("❌ Geçersiz not numarası.")
            sesli_konus("Geçersiz not numarası.")
            return

        silinen_not = notlar.pop(secim - 1)
        notlari_kaydet(notlar)

        print("🗑️ Silinen not:", silinen_not)
        sesli_konus("Not başarıyla silindi.")

    except ValueError:
        print("❌ Lütfen yalnızca sayı giriniz.")
        sesli_konus("Lütfen yalnızca sayı giriniz.")


def tum_notlari_sil():
    notlar = notlari_oku()

    if not notlar:
        print("\n📭 Silinecek not bulunamadı.")
        sesli_konus("Silinecek not bulunamadı.")
        return

    onay = input(
        "Tüm notları silmek istediğinize emin misiniz? (e/h): "
    ).strip().lower()

    if onay == "e":
        notlari_kaydet([])

        print("🗑️ Tüm notlar silindi.")
        sesli_konus("Tüm notlar silindi.")

    else:
        print("İşlem iptal edildi.")
        sesli_konus("İşlem iptal edildi.")


def ana_menu():
    while True:
        print("\n================================")
        print("      GELİŞMİŞ NOT DEFTERİ")
        print("================================")
        print("1 - Not ekle")
        print("2 - Notları göster")
        print("3 - Not sil")
        print("4 - Tüm notları sil")
        print("5 - Çıkış")

        sesli_konus("Hangi işlemi yapmak istiyorsunuz?")

        secim = input("Seçiminiz: ").strip()

        if secim == "1":
            not_ekle()

        elif secim == "2":
            notlari_goster()

        elif secim == "3":
            not_sil()

        elif secim == "4":
            tum_notlari_sil()

        elif secim == "5":
            print("Program kapatılıyor.")
            sesli_konus("Program kapatılıyor.")
            break

        else:
            print("❌ Geçersiz seçim yaptınız.")
            sesli_konus("Geçersiz seçim yaptınız.")


giris_yap()
ana_menu()