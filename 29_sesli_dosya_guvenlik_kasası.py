# Proje 29 - Sesli Dosya Güvenlik Kasası
# Sürüm 1.0

import hashlib
import os
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, simpledialog


KASA_KLASORU = "guvenlik_kasasi"
SIFRE_DOSYASI = "kasa_sifresi.txt"


def sesli_konus(metin):
    subprocess.run(
        ["say", metin],
        check=False
    )


def gizli_sifre_al(baslik, mesaj):
    pencere = tk.Tk()
    pencere.withdraw()
    pencere.attributes("-topmost", True)

    sifre = simpledialog.askstring(
        baslik,
        mesaj,
        show="*",
        parent=pencere
    )

    pencere.destroy()

    if sifre is None:
        return ""

    return sifre


def sifre_ozeti_olustur(sifre):
    return hashlib.sha256(
        sifre.encode("utf-8")
    ).hexdigest()


def kasa_hazirla():
    os.makedirs(
        KASA_KLASORU,
        exist_ok=True
    )


def kasa_sifresi_var_mi():
    return os.path.exists(SIFRE_DOSYASI)


def kasa_sifresi_olustur():
    print("\n================================")
    print("       KASA ŞİFRESİ OLUŞTUR")
    print("================================")

    sesli_konus("Yeni kasa şifresi oluşturunuz.")

    sifre = gizli_sifre_al(
        "Kasa Şifresi",
        "Yeni kasa şifresini giriniz:"
    )

    sifre_tekrar = gizli_sifre_al(
        "Şifre Doğrulama",
        "Kasa şifresini tekrar giriniz:"
    )

    if not sifre:
        print("❌ Şifre boş bırakılamaz.")
        sesli_konus("Şifre boş bırakılamaz.")
        return False

    if len(sifre) < 4:
        print("❌ Şifre en az 4 karakter olmalıdır.")
        sesli_konus(
            "Şifre en az dört karakter olmalıdır."
        )
        return False

    if sifre != sifre_tekrar:
        print("❌ Şifreler uyuşmuyor.")
        sesli_konus("Şifreler uyuşmuyor.")
        return False

    with open(
        SIFRE_DOSYASI,
        "w",
        encoding="utf-8"
    ) as dosya:
        dosya.write(
            sifre_ozeti_olustur(sifre)
        )

    print("✅ Kasa şifresi başarıyla oluşturuldu.")
    sesli_konus(
        "Kasa şifresi başarıyla oluşturuldu."
    )

    return True


def kasa_girisi():
    try:
        with open(
            SIFRE_DOSYASI,
            "r",
            encoding="utf-8"
        ) as dosya:
            kayitli_ozet = dosya.read().strip()

    except FileNotFoundError:
        print("❌ Kasa şifre dosyası bulunamadı.")
        sesli_konus("Kasa şifre dosyası bulunamadı.")
        return False

    hak = 3

    print("\n================================")
    print("        GÜVENLİK KASASI GİRİŞİ")
    print("================================")

    sesli_konus("Güvenlik kasasına giriş yapınız.")

    while hak > 0:
        sifre = gizli_sifre_al(
            "Güvenlik Kasası",
            "Kasa şifresini giriniz:"
        )

        if sifre_ozeti_olustur(sifre) == kayitli_ozet:
            print("✅ Kasa başarıyla açıldı.")
            sesli_konus("Kasa başarıyla açıldı.")
            return True

        hak -= 1

        print("❌ Hatalı şifre.")
        print("Kalan giriş hakkı:", hak)

        if hak > 0:
            sesli_konus(
                f"Hatalı şifre. Kalan giriş hakkınız {hak}."
            )

    print("\n🔒 Kasa kilitlendi.")
    sesli_konus(
        "Üç kez hatalı şifre girildi. Kasa kilitlendi."
    )

    return False


def dosya_kasaya_ekle():
    pencere = tk.Tk()
    pencere.withdraw()
    pencere.attributes("-topmost", True)

    kaynak_dosya = filedialog.askopenfilename(
        title="Kasaya eklenecek dosyayı seçiniz",
        parent=pencere
    )

    pencere.destroy()

    if not kaynak_dosya:
        print("İşlem iptal edildi.")
        sesli_konus("İşlem iptal edildi.")
        return

    dosya_adi = os.path.basename(kaynak_dosya)

    hedef_dosya = os.path.join(
        KASA_KLASORU,
        dosya_adi
    )

    if os.path.exists(hedef_dosya):
        print("❌ Bu dosya kasada zaten bulunuyor.")
        sesli_konus(
            "Bu dosya kasada zaten bulunuyor."
        )
        return

    try:
        shutil.copy2(
            kaynak_dosya,
            hedef_dosya
        )

        print("✅ Dosya kasaya kopyalandı:", dosya_adi)
        sesli_konus("Dosya başarıyla kasaya eklendi.")

    except OSError:
        print("❌ Dosya kasaya eklenemedi.")
        sesli_konus("Dosya kasaya eklenemedi.")


def kasadaki_dosyalari_goster():
    dosyalar = os.listdir(KASA_KLASORU)

    if not dosyalar:
        print("\n📭 Kasada dosya bulunmuyor.")
        sesli_konus("Kasada dosya bulunmuyor.")
        return

    print("\n===== KASADAKİ DOSYALAR =====")

    for numara, dosya_adi in enumerate(
        dosyalar,
        start=1
    ):
        print(f"{numara} - {dosya_adi}")

    sesli_konus(
        f"Kasada toplam {len(dosyalar)} dosya bulundu."
    )


def kasadan_dosya_sil():
    dosyalar = os.listdir(KASA_KLASORU)

    if not dosyalar:
        print("\n📭 Kasada silinecek dosya bulunmuyor.")
        sesli_konus(
            "Kasada silinecek dosya bulunmuyor."
        )
        return

    print("\n===== KASADAKİ DOSYALAR =====")

    for numara, dosya_adi in enumerate(
        dosyalar,
        start=1
    ):
        print(f"{numara} - {dosya_adi}")

    try:
        secim = int(
            input("Silinecek dosyanın numarası: ")
        )

        if secim < 1 or secim > len(dosyalar):
            print("❌ Geçersiz dosya numarası.")
            sesli_konus("Geçersiz dosya numarası.")
            return

        secilen_dosya = dosyalar[secim - 1]

        onay = input(
            f"{secilen_dosya} silinsin mi? (e/h): "
        ).strip().lower()

        if onay != "e":
            print("İşlem iptal edildi.")
            sesli_konus("İşlem iptal edildi.")
            return

        dosya_yolu = os.path.join(
            KASA_KLASORU,
            secilen_dosya
        )

        os.remove(dosya_yolu)

        print("🗑️ Dosya kasadan silindi:", secilen_dosya)
        sesli_konus("Dosya kasadan başarıyla silindi.")

    except ValueError:
        print("❌ Lütfen yalnızca sayı giriniz.")
        sesli_konus("Lütfen yalnızca sayı giriniz.")


def ana_menu():
    while True:
        print("\n================================")
        print("       DOSYA GÜVENLİK KASASI")
        print("================================")
        print("1 - Dosyayı kasaya ekle")
        print("2 - Kasadaki dosyaları göster")
        print("3 - Kasadan dosya sil")
        print("4 - Çıkış")

        sesli_konus("Hangi işlemi yapmak istiyorsunuz?")

        secim = input("Seçiminiz: ").strip()

        if secim == "1":
            dosya_kasaya_ekle()

        elif secim == "2":
            kasadaki_dosyalari_goster()

        elif secim == "3":
            kasadan_dosya_sil()

        elif secim == "4":
            print("\n✅ Çıkış yapıldı.")
            sesli_konus("Çıkış yapıldı.")
            break

        else:
            print("\n❌ Hatalı giriş yaptınız.")
            sesli_konus("Hatalı giriş yaptınız.")


kasa_hazirla()

if not kasa_sifresi_var_mi():
    if not kasa_sifresi_olustur():
        sys.exit()

if kasa_girisi():
    ana_menu()