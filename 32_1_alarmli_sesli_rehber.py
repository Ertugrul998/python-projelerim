# Proje 32.1 - Alarmlı Sesli Rehber
# Sürüm 1.0

import getpass
import hashlib
import json
import os
import subprocess
import sys
import threading
import time


REHBER_DOSYASI = "rehber.json"
SIFRE_DOSYASI = "rehber_sifresi.json"
ALARM_DOSYASI = "/System/Library/Sounds/Sosumi.aiff"

sesli_mod = False


# ==================================================
# SESLİ KONUŞMA
# ==================================================

def sesli_konus(metin):
    """Sesli mod açıksa Mac konuşur."""

    if sesli_mod:
        subprocess.run(
            ["say", metin],
            check=False
        )


# ==================================================
# SES MODU
# ==================================================

def mod_sec():
    """Sesli veya sessiz modu seçtirir."""

    global sesli_mod

    while True:
        print("\n========================")
        print("       SES MODU")
        print("========================")
        print("1 - Sesli mod")
        print("2 - Sessiz mod")

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


# ==================================================
# ŞİFRE İŞLEMLERİ
# ==================================================

def sifreyi_hashle(sifre):
    """Şifreyi doğrudan değil, özetlenmiş biçimde saklar."""

    return hashlib.sha256(
        sifre.encode("utf-8")
    ).hexdigest()


def sifre_kaydi_var_mi():
    """Daha önce rehber şifresi oluşturulmuş mu kontrol eder."""

    return os.path.exists(SIFRE_DOSYASI)


def ilk_sifreyi_olustur():
    """Program ilk kez açıldığında kullanıcıya şifre oluşturur."""

    print("\n================================")
    print("     REHBER ŞİFRESİ OLUŞTUR")
    print("================================")

    sesli_konus(
        "Rehberinizi korumak için yeni bir şifre oluşturunuz."
    )

    while True:
        sifre = getpass.getpass(
            "Yeni şifrenizi giriniz: "
        )

        sifre_tekrar = getpass.getpass(
            "Şifrenizi tekrar giriniz: "
        )

        if not sifre:
            print("❌ Şifre boş bırakılamaz.")
            sesli_konus("Şifre boş bırakılamaz.")
            continue

        if len(sifre) < 4:
            print("❌ Şifre en az 4 karakter olmalıdır.")
            sesli_konus(
                "Şifre en az dört karakter olmalıdır."
            )
            continue

        if sifre != sifre_tekrar:
            print("❌ Şifreler birbiriyle uyuşmuyor.")
            sesli_konus(
                "Şifreler birbiriyle uyuşmuyor."
            )
            continue

        sifre_bilgisi = {
            "sifre_ozeti": sifreyi_hashle(sifre)
        }

        with open(
            SIFRE_DOSYASI,
            "w",
            encoding="utf-8"
        ) as dosya:
            json.dump(
                sifre_bilgisi,
                dosya,
                ensure_ascii=False,
                indent=4
            )

        print("✅ Rehber şifresi oluşturuldu.")
        sesli_konus(
            "Rehber şifresi başarıyla oluşturuldu."
        )
        return


def kayitli_sifreyi_oku():
    """Kaydedilmiş şifre özetini okur."""

    try:
        with open(
            SIFRE_DOSYASI,
            "r",
            encoding="utf-8"
        ) as dosya:
            bilgiler = json.load(dosya)

        return bilgiler.get("sifre_ozeti")

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ):
        return None


# ==================================================
# ALARM VE KİLİT
# ==================================================

def alarm_sesi(durdurma_sinyali):
    """Enter tuşuna basılana kadar alarm çalar."""

    while not durdurma_sinyali.is_set():
        subprocess.run(
            ["afplay", ALARM_DOSYASI],
            check=False
        )

        time.sleep(0.2)


def sistemi_kilitle():
    """Üç yanlış şifreden sonra alarmı çalıştırır."""

    print("\n🚨 Üç kez yanlış şifre girildi!")
    print("🔒 Rehber sistemi kilitlendi.")
    print("⏎ Alarmı durdurmak için Enter tuşuna basınız.")

    sesli_konus(
        "Dikkat. Üç kez yanlış şifre girildi. "
        "Rehber sistemi kilitlendi. "
        "Alarmı durdurmak için Enter tuşuna basınız."
    )

    durdurma_sinyali = threading.Event()

    alarm_thread = threading.Thread(
        target=alarm_sesi,
        args=(durdurma_sinyali,),
        daemon=True
    )

    alarm_thread.start()

    input()

    durdurma_sinyali.set()
    alarm_thread.join(timeout=2)

    print("\n🔕 Alarm durduruldu.")
    print("🔒 Sistem kapatılıyor.")

    sesli_konus(
        "Alarm durduruldu. Sistem kapatılıyor."
    )

    sys.exit()


def sifreyi_dogrula():
    """Kullanıcıya üç şifre hakkı verir."""

    kayitli_sifre = kayitli_sifreyi_oku()

    if kayitli_sifre is None:
        print("❌ Şifre bilgileri okunamadı.")
        sesli_konus("Şifre bilgileri okunamadı.")
        return False

    kalan_hak = 3

    while kalan_hak > 0:
        girilen_sifre = getpass.getpass(
            "Rehber şifresini giriniz: "
        )

        if sifreyi_hashle(girilen_sifre) == kayitli_sifre:
            print("✅ Şifre doğru.")
            sesli_konus("Şifre doğru.")
            return True

        kalan_hak -= 1

        print("❌ Şifre yanlış.")
        print("Kalan giriş hakkı:", kalan_hak)

        if kalan_hak > 0:
            sesli_konus(
                f"Şifre yanlış. "
                f"Kalan giriş hakkınız {kalan_hak}."
            )

    sistemi_kilitle()

    return False


# ==================================================
# REHBER DOSYA İŞLEMLERİ
# ==================================================

def rehberi_oku():
    """Rehberdeki kişileri JSON dosyasından okur."""

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
        print("❌ Rehber dosyası okunamadı.")
        sesli_konus("Rehber dosyası okunamadı.")
        return {}


def rehberi_kaydet(rehber):
    """Rehber bilgilerini JSON dosyasına kaydeder."""

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


# ==================================================
# REHBER FONKSİYONLARI
# ==================================================

def kisi_ekle():
    """Rehbere yeni kişi ekler."""

    rehber = rehberi_oku()

    print("\n===== KİŞİ EKLE =====")

    isim = input("Kişinin adı: ").strip()
    telefon = input("Telefon numarası: ").strip()

    if not isim or not telefon:
        print("❌ İsim ve telefon boş bırakılamaz.")
        sesli_konus(
            "İsim ve telefon boş bırakılamaz."
        )
        return

    bulunan_isim = None

    for kayitli_isim in rehber:
        if kayitli_isim.lower() == isim.lower():
            bulunan_isim = kayitli_isim
            break

    if bulunan_isim is not None:
        print("⚠️ Bu kişi rehberde zaten kayıtlı.")

        onay = input(
            "Telefon numarası güncellensin mi? (e/h): "
        ).strip().lower()

        if onay != "e":
            print("İşlem iptal edildi.")
            sesli_konus("İşlem iptal edildi.")
            return

        del rehber[bulunan_isim]

    rehber[isim] = telefon
    rehberi_kaydet(rehber)

    print("✅ Kişi rehbere kaydedildi.")
    sesli_konus("Kişi rehbere kaydedildi.")


def rehberi_goster():
    """Doğru şifre girilirse rehber kayıtlarını gösterir."""

    print("\n===== ŞİFRE KONTROLÜ =====")
    sesli_konus(
        "Rehberi görüntülemek için şifrenizi giriniz."
    )

    if not sifreyi_dogrula():
        return

    rehber = rehberi_oku()

    if not rehber:
        print("📭 Rehber boş.")
        sesli_konus("Rehber boş.")
        return

    print("\n================================")
    print("             REHBER")
    print("================================")

    sirali_kisiler = sorted(
        rehber.items(),
        key=lambda kayit: kayit[0].lower()
    )

    for sira, (isim, telefon) in enumerate(
        sirali_kisiler,
        start=1
    ):
        print(f"{sira} - {isim}: {telefon}")

    print("================================")

    sesli_konus(
        f"Rehberde toplam {len(rehber)} kişi bulunuyor."
    )


def kisi_ara():
    """İsme göre rehberde kişi arar."""

    rehber = rehberi_oku()

    print("\n===== KİŞİ ARA =====")

    aranan_isim = input(
        "Aranacak kişinin adı: "
    ).strip()

    if not aranan_isim:
        print("❌ Aranacak isim boş bırakılamaz.")
        sesli_konus(
            "Aranacak isim boş bırakılamaz."
        )
        return

    for isim, telefon in rehber.items():
        if isim.lower() == aranan_isim.lower():
            print(f"✅ {isim}: {telefon}")
            sesli_konus(f"{isim} bulundu.")
            return

    print("❌ Kişi bulunamadı.")
    sesli_konus("Kişi bulunamadı.")


def kisi_sil():
    """Şifre doğrulandıktan sonra kişiyi siler."""

    print("\n===== ŞİFRE KONTROLÜ =====")
    sesli_konus(
        "Kişi silmek için şifrenizi giriniz."
    )

    if not sifreyi_dogrula():
        return

    rehber = rehberi_oku()

    if not rehber:
        print("📭 Rehber boş.")
        sesli_konus("Rehber boş.")
        return

    print("\n===== KİŞİ SİL =====")

    silinecek_isim = input(
        "Silinecek kişinin adı: "
    ).strip()

    bulunan_isim = None

    for isim in rehber:
        if isim.lower() == silinecek_isim.lower():
            bulunan_isim = isim
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

    print("🗑️ Kişi rehberden silindi.")
    sesli_konus("Kişi rehberden silindi.")


# ==================================================
# ANA MENÜ
# ==================================================

def ana_menu():
    """Alarmlı rehberin ana menüsünü çalıştırır."""

    sesli_konus(
        "Alarmlı sesli rehber sistemine hoş geldiniz."
    )

    while True:
        print("\n================================")
        print("       ALARMLI SESLİ REHBER")
        print("================================")
        print("1 - Kişi ekle")
        print("2 - Rehberi göster")
        print("3 - Kişi ara")
        print("4 - Kişi sil")
        print("5 - Ses modunu değiştir")
        print("6 - Çıkış")

        sesli_konus(
            "Hangi işlemi yapmak istiyorsunuz?"
        )

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
            print("\n👋 Çıkış yapıldı.")
            sesli_konus("Çıkış yapıldı.")
            break

        else:
            print("\n❌ Hatalı menü seçimi yaptınız.")
            sesli_konus(
                "Hatalı menü seçimi yaptınız."
            )


# ==================================================
# PROGRAMI BAŞLAT
# ==================================================

mod_sec()

if not sifre_kaydi_var_mi():
    ilk_sifreyi_olustur()

ana_menu()