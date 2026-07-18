import json
import os
import subprocess


REHBER_DOSYASI = "rehber.json"
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


def rehberi_oku():
    if not os.path.exists(REHBER_DOSYASI):
        return {}

    try:
        with open(
            REHBER_DOSYASI,
            "r",
            encoding="utf-8"
        ) as dosya:
            return json.load(dosya)

    except json.JSONDecodeError:
        return {}


def rehberi_kaydet(rehber):
    with open(
        REHBER_DOSYASI,
        "w",
        encoding="utf-8"
    ) as dosya:
        json.dump(
            rehber,
            dosya,
            ensure_ascii=False,
            indent=4
        )


def kisi_ekle():
    rehber = rehberi_oku()

    isim = input("İsim: ").strip()
    telefon = input("Telefon: ").strip()

    if not isim or not telefon:
        print("❌ Boş alan bırakılamaz.")
        sesli_konus("Boş alan bırakılamaz.")
        return

    if isim in rehber:
        onay = input(
            "Bu kişi zaten kayıtlı. Güncellensin mi? (e/h): "
        ).strip().lower()

        if onay != "e":
            print("İşlem iptal edildi.")
            sesli_konus("İşlem iptal edildi.")
            return

    rehber[isim] = telefon
    rehberi_kaydet(rehber)

    print("✅ Kişi kaydedildi.")
    sesli_konus("Kişi kaydedildi.")


def rehberi_goster():
    rehber = rehberi_oku()

    if not rehber:
        print("📭 Rehber boş.")
        sesli_konus("Rehber boş.")
        return

    print("\n===== REHBER =====")

    sirali_rehber = sorted(
        rehber.items(),
        key=lambda kayit: kayit[0].lower()
    )

    for sira, (isim, telefon) in enumerate(
        sirali_rehber,
        start=1
    ):
        print(f"{sira} - {isim}: {telefon}")

    sesli_konus(
        f"Rehberde toplam {len(rehber)} kişi bulunuyor."
    )


def kisi_ara():
    rehber = rehberi_oku()

    isim = input("Aranacak kişi: ").strip()

    bulunan_kisi = None

    for kayitli_isim, telefon in rehber.items():
        if kayitli_isim.lower() == isim.lower():
            bulunan_kisi = (kayitli_isim, telefon)
            break

    if bulunan_kisi:
        kayitli_isim, telefon = bulunan_kisi

        print(f"✅ {kayitli_isim}: {telefon}")
        sesli_konus(f"{kayitli_isim} bulundu.")

    else:
        print("❌ Kişi bulunamadı.")
        sesli_konus("Kişi bulunamadı.")


def kisi_sil():
    rehber = rehberi_oku()

    isim = input("Silinecek kişi: ").strip()

    bulunan_isim = None

    for kayitli_isim in rehber:
        if kayitli_isim.lower() == isim.lower():
            bulunan_isim = kayitli_isim
            break

    if bulunan_isim is None:
        print("❌ Kişi bulunamadı.")
        sesli_konus("Kişi bulunamadı.")
        return

    onay = input(
        f"{bulunan_isim} silinsin mi? (e/h): "
    ).strip().lower()

    if onay != "e":
        print("İşlem iptal edildi.")
        sesli_konus("İşlem iptal edildi.")
        return

    del rehber[bulunan_isim]
    rehberi_kaydet(rehber)

    print("🗑️ Kişi silindi.")
    sesli_konus("Kişi silindi.")


def ana_menu():
    while True:
        print("\n========================")
        print("      SESLİ REHBER")
        print("========================")
        print("1 - Kişi ekle")
        print("2 - Rehberi göster")
        print("3 - Kişi ara")
        print("4 - Kişi sil")
        print("5 - Ses modunu değiştir")
        print("6 - Çıkış")

        sesli_konus("Bir işlem seçiniz.")

        secim = input("Seçiminiz: ").strip()

        if secim == "1":
            kisi_ekle()

        elif secim == "2":
            rehberi_goster()

        elif secim == "3":
            kisi_ara()

        elif secim == "4":
            kisi_sil()

        elif secim == "5":
            mod_sec()

        elif secim == "6":
            print("👋 Çıkış yapıldı.")
            sesli_konus("Çıkış yapıldı.")
            break

        else:
            print("❌ Hatalı giriş yaptınız.")
            sesli_konus("Hatalı giriş yaptınız.")


mod_sec()
ana_menu()
