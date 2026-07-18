# Proje 28 - Sesli Mini Dosya Yöneticisi
# Sürüm 1.0

import os
import shutil
import subprocess


CALISMA_KLASORU = "dosya_yonetici_alani"


def sesli_konus(metin):
    subprocess.run(
        ["say", metin],
        check=False
    )


def klasoru_hazirla():
    os.makedirs(
        CALISMA_KLASORU,
        exist_ok=True
    )


def dosyalari_goster():
    dosyalar = os.listdir(CALISMA_KLASORU)

    if not dosyalar:
        print("\n📭 Çalışma klasörü boş.")
        sesli_konus("Çalışma klasörü boş.")
        return

    print("\n===== DOSYA VE KLASÖRLER =====")

    for numara, dosya_adi in enumerate(
        dosyalar,
        start=1
    ):
        tam_yol = os.path.join(
            CALISMA_KLASORU,
            dosya_adi
        )

        if os.path.isdir(tam_yol):
            tur = "KLASÖR"
        else:
            tur = "DOSYA"

        print(f"{numara} - [{tur}] {dosya_adi}")

    sesli_konus(
        f"Toplam {len(dosyalar)} öğe bulundu."
    )


def dosya_olustur():
    print("\n===== DOSYA OLUŞTUR =====")

    sesli_konus("Oluşturmak istediğiniz dosyanın adını yazınız.")

    dosya_adi = input(
        "Dosya adı: "
    ).strip()

    if not dosya_adi:
        print("❌ Dosya adı boş bırakılamaz.")
        sesli_konus("Dosya adı boş bırakılamaz.")
        return

    tam_yol = os.path.join(
        CALISMA_KLASORU,
        dosya_adi
    )

    if os.path.exists(tam_yol):
        print("❌ Bu isimde bir dosya veya klasör zaten var.")
        sesli_konus(
            "Bu isimde bir dosya veya klasör zaten var."
        )
        return

    icerik = input(
        "Dosyanın içeriğini yazınız: "
    )

    with open(
        tam_yol,
        "w",
        encoding="utf-8"
    ) as dosya:
        dosya.write(icerik)

    print("✅ Dosya başarıyla oluşturuldu.")
    sesli_konus("Dosya başarıyla oluşturuldu.")


def klasor_olustur():
    print("\n===== KLASÖR OLUŞTUR =====")

    sesli_konus(
        "Oluşturmak istediğiniz klasörün adını yazınız."
    )

    klasor_adi = input(
        "Klasör adı: "
    ).strip()

    if not klasor_adi:
        print("❌ Klasör adı boş bırakılamaz.")
        sesli_konus("Klasör adı boş bırakılamaz.")
        return

    tam_yol = os.path.join(
        CALISMA_KLASORU,
        klasor_adi
    )

    if os.path.exists(tam_yol):
        print("❌ Bu isimde bir dosya veya klasör zaten var.")
        sesli_konus(
            "Bu isimde bir dosya veya klasör zaten var."
        )
        return

    os.makedirs(tam_yol)

    print("✅ Klasör başarıyla oluşturuldu.")
    sesli_konus("Klasör başarıyla oluşturuldu.")


def dosya_oku():
    print("\n===== DOSYA OKU =====")

    dosya_adi = input(
        "Okunacak dosyanın adı: "
    ).strip()

    tam_yol = os.path.join(
        CALISMA_KLASORU,
        dosya_adi
    )

    try:
        with open(
            tam_yol,
            "r",
            encoding="utf-8"
        ) as dosya:
            icerik = dosya.read()

        print("\n===== DOSYA İÇERİĞİ =====")

        if icerik:
            print(icerik)
        else:
            print("Dosya boş.")

        sesli_konus("Dosya içeriği gösterildi.")

    except FileNotFoundError:
        print("❌ Dosya bulunamadı.")
        sesli_konus("Dosya bulunamadı.")

    except IsADirectoryError:
        print("❌ Seçilen öğe bir klasördür.")
        sesli_konus("Seçilen öğe bir klasördür.")


def oge_sil():
    print("\n===== DOSYA VEYA KLASÖR SİL =====")

    ad = input(
        "Silinecek dosya veya klasör adı: "
    ).strip()

    tam_yol = os.path.join(
        CALISMA_KLASORU,
        ad
    )

    if not os.path.exists(tam_yol):
        print("❌ Dosya veya klasör bulunamadı.")
        sesli_konus("Dosya veya klasör bulunamadı.")
        return

    onay = input(
        "Bu öğe silinsin mi? (e/h): "
    ).strip().lower()

    if onay != "e":
        print("İşlem iptal edildi.")
        sesli_konus("İşlem iptal edildi.")
        return

    if os.path.isdir(tam_yol):
        shutil.rmtree(tam_yol)
    else:
        os.remove(tam_yol)

    print("🗑️ Öğe başarıyla silindi.")
    sesli_konus("Öğe başarıyla silindi.")


def ana_menu():
    klasoru_hazirla()

    sesli_konus(
        "Mini dosya yöneticisine hoş geldiniz."
    )

    while True:
        print("\n================================")
        print("       MİNİ DOSYA YÖNETİCİSİ")
        print("================================")
        print("1 - Dosya ve klasörleri göster")
        print("2 - Dosya oluştur")
        print("3 - Klasör oluştur")
        print("4 - Dosya oku")
        print("5 - Dosya veya klasör sil")
        print("6 - Çıkış")

        sesli_konus("Hangi işlemi yapmak istiyorsunuz?")

        secim = input("Seçiminiz: ").strip()

        if secim == "1":
            dosyalari_goster()

        elif secim == "2":
            dosya_olustur()

        elif secim == "3":
            klasor_olustur()

        elif secim == "4":
            dosya_oku()

        elif secim == "5":
            oge_sil()

        elif secim == "6":
            print("\n✅ Çıkış yapıldı.")
            sesli_konus("Çıkış yapıldı.")
            break

        else:
            print("\n❌ Hatalı giriş yaptınız.")
            sesli_konus("Hatalı giriş yaptınız.")


ana_menu()