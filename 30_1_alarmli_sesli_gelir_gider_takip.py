# Proje 30 - Alarmsız Sesli/Sessiz Gelir Gider Takip Sistemi
# Sürüm 1.1

import datetime
import subprocess
import sys
import threading
import time

KAYIT_DOSYASI = "gelir_gider_kayitlari.txt"
AlARM_DOSYASI = "/System/Library/Sounds/Sosumi.aiff"
sesli_mod = False


def sesli_konus(metin):
    """Sesli mod açıksa Mac'in say komutuyla konuşur."""
    if sesli_mod:
        subprocess.run(
            ["say", metin],
            check=False
        )


def mod_sec():
    global sesli_mod

    while True:
        print("\n================================")
        print("           MOD SEÇİMİ")
        print("================================")
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


def kayitlari_oku():
    try:
        with open(
            KAYIT_DOSYASI,
            "r",
            encoding="utf-8"
        ) as dosya:
            return [
                satir.strip()
                for satir in dosya
                if satir.strip()
            ]

    except FileNotFoundError:
        return []


def para_miktari_al(mesaj):
    try:
        miktar_metni = input(mesaj).strip().replace(",", ".")
        miktar = float(miktar_metni)

        if miktar <= 0:
            print("❌ Miktar sıfırdan büyük olmalıdır.")
            sesli_konus("Miktar sıfırdan büyük olmalıdır.")
            return None

        return miktar

    except ValueError:
        print("❌ Geçerli bir para miktarı giriniz.")
        sesli_konus("Geçerli bir para miktarı giriniz.")
        return None


def kayit_ekle(kayit_turu):
    print(f"\n===== {kayit_turu} EKLE =====")

    sesli_konus(
        f"{kayit_turu.lower()} açıklamasını yazınız."
    )

    aciklama = input(
        f"{kayit_turu.title()} açıklaması: "
    ).strip()

    if not aciklama:
        print("❌ Açıklama boş bırakılamaz.")
        sesli_konus("Açıklama boş bırakılamaz.")
        return

    miktar = para_miktari_al(
        f"{kayit_turu.title()} miktarı: "
    )

    if miktar is None:
        return

    tarih = datetime.datetime.now().strftime(
        "%d.%m.%Y %H:%M"
    )

    kayit = (
        f"{kayit_turu}|{aciklama}|"
        f"{miktar:.2f}|{tarih}"
    )

    with open(
        KAYIT_DOSYASI,
        "a",
        encoding="utf-8"
    ) as dosya:
        dosya.write(kayit + "\n")

    print(f"✅ {kayit_turu.title()} başarıyla kaydedildi.")

    sesli_konus(
        f"{kayit_turu.lower()} başarıyla kaydedildi."
    )


def gelir_ekle():
    kayit_ekle("GELİR")


def gider_ekle():
    kayit_ekle("GİDER")


def kayitlari_goster():
    kayitlar = kayitlari_oku()

    if not kayitlar:
        print("\n📭 Gelir veya gider kaydı bulunamadı.")
        sesli_konus("Gelir veya gider kaydı bulunamadı.")
        return

    print("\n==============================================")
    print("          GELİR VE GİDER KAYITLARI")
    print("==============================================")

    gosterilen_kayit = 0

    for numara, kayit in enumerate(
        kayitlar,
        start=1
    ):
        parcalar = kayit.split("|")

        if len(parcalar) != 4:
            continue

        tur, aciklama, miktar, tarih = parcalar

        print(
            f"{numara} - {tur} | "
            f"{aciklama} | {miktar} TL | {tarih}"
        )

        gosterilen_kayit += 1

    print("==============================================")

    sesli_konus(
        f"Toplam {gosterilen_kayit} kayıt gösterildi."
    )


def mali_durumu_goster():
    kayitlar = kayitlari_oku()

    toplam_gelir = 0.0
    toplam_gider = 0.0

    for kayit in kayitlar:
        parcalar = kayit.split("|")

        if len(parcalar) != 4:
            continue

        tur = parcalar[0]

        try:
            miktar = float(parcalar[2])
        except ValueError:
            continue

        if tur == "GELİR":
            toplam_gelir += miktar

        elif tur == "GİDER":
            toplam_gider += miktar

    bakiye = toplam_gelir - toplam_gider

    print("\n================================")
    print("           MALİ DURUM")
    print("================================")
    print(f"Toplam gelir : {toplam_gelir:.2f} TL")
    print(f"Toplam gider : {toplam_gider:.2f} TL")
    print(f"Kalan bakiye : {bakiye:.2f} TL")

    if bakiye > 0:
        print("✅ Bakiyeniz pozitif.")

    elif bakiye < 0:
        print("⚠️ Gideriniz gelirinizden fazla.")

    else:
        print("ℹ️ Gelir ve gideriniz eşit.")

    sesli_konus(
        f"Toplam geliriniz {toplam_gelir:.2f} Türk lirası. "
        f"Toplam gideriniz {toplam_gider:.2f} Türk lirası. "
        f"Kalan bakiyeniz {bakiye:.2f} Türk lirası."
    )


def kayit_sil():
    kayitlar = kayitlari_oku()

    if not kayitlar:
        print("\n📭 Silinecek kayıt bulunamadı.")
        sesli_konus("Silinecek kayıt bulunamadı.")
        return

    print("\n===== KAYITLAR =====")

    for numara, kayit in enumerate(
        kayitlar,
        start=1
    ):
        parcalar = kayit.split("|")

        if len(parcalar) == 4:
            tur, aciklama, miktar, tarih = parcalar

            print(
                f"{numara} - {tur} | "
                f"{aciklama} | {miktar} TL | {tarih}"
            )

    try:
        secim = int(
            input("Silmek istediğiniz kaydın numarası: ")
        )

        if secim < 1 or secim > len(kayitlar):
            print("❌ Geçersiz kayıt numarası.")
            sesli_konus("Geçersiz kayıt numarası.")
            return

        silinen_kayit = kayitlar.pop(secim - 1)

        with open(
            KAYIT_DOSYASI,
            "w",
            encoding="utf-8"
        ) as dosya:
            for kayit in kayitlar:
                dosya.write(kayit + "\n")

        print("🗑️ Kayıt başarıyla silindi.")
        print("Silinen kayıt:", silinen_kayit)

        sesli_konus("Kayıt başarıyla silindi.")

    except ValueError:
        print("❌ Lütfen yalnızca sayı giriniz.")
        sesli_konus("Lütfen yalnızca sayı giriniz.")


def tum_kayitlari_sil():
    kayitlar = kayitlari_oku()

    if not kayitlar:
        print("\n📭 Silinecek kayıt bulunamadı.")
        sesli_konus("Silinecek kayıt bulunamadı.")
        return

    onay = input(
        "Tüm gelir ve gider kayıtları silinsin mi? (e/h): "
    ).strip().lower()

    if onay == "e":
        with open(
            KAYIT_DOSYASI,
            "w",
            encoding="utf-8"
        ):
            pass

        print("🗑️ Tüm kayıtlar silindi.")
        sesli_konus("Tüm kayıtlar silindi.")

    else:
        print("İşlem iptal edildi.")
        sesli_konus("İşlem iptal edildi.")

def alarm_sesi(durdurma_sinyali):
    while not durdurma_sinyali.is_set():
        subprocess.run(
            ["afplay", AlARM_DOSYASI],
            check=False
        )
        time.sleep(0.2)


def sistemi_kilitle():
    print("\n🚨 Üç kez hatalı seçim yapıldı!")
    print("🔒 Gelir gider sistemi kilitlendi.")
    print("⏎ Alarmı durdurmak için Enter tuşuna basınız.")

    sesli_konus(
        "Dikkat. Üç kez hatalı seçim yapıldı. "
        "Gelir gider sistemi kilitlendi. "
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
    print("Program kapatılıyor.")

    sesli_konus(
        "Alarm durduruldu. Program kapatılıyor."
    )

    sys.exit()

def ana_menu():
    hatali_secim_hakki = 3

    sesli_konus(
        "Alarmlı gelir gider takip sistemine hoş geldiniz."
    )

    while True:
        print("\n================================")
        print("   ALARMLI GELİR GİDER SİSTEMİ")
        print("================================")
        print("1 - Gelir ekle")
        print("2 - Gider ekle")
        print("3 - Kayıtları göster")
        print("4 - Mali durumu göster")
        print("5 - Kayıt sil")
        print("6 - Tüm kayıtları sil")
        print("7 - Ses modunu değiştir")
        print("8 - Çıkış")

        sesli_konus("Hangi işlemi yapmak istiyorsunuz?")

        secim = input("Seçiminiz: ").strip()

        if secim == "1":
            gelir_ekle()
            hatali_secim_hakki = 3

        elif secim == "2":
            gider_ekle()
            hatali_secim_hakki = 3

        elif secim == "3":
            kayitlari_goster()
            hatali_secim_hakki = 3

        elif secim == "4":
            mali_durumu_goster()
            hatali_secim_hakki = 3

        elif secim == "5":
            kayit_sil()
            hatali_secim_hakki = 3

        elif secim == "6":
            tum_kayitlari_sil()
            hatali_secim_hakki = 3

        elif secim == "7":
            mod_sec()
            hatali_secim_hakki = 3

        elif secim == "8":
            print("\n✅ Çıkış yapıldı.")
            sesli_konus("Çıkış yapıldı.")
            break

        else:
            hatali_secim_hakki -= 1

            print("\n❌ Hatalı giriş yaptınız.")
            print("Kalan hak:", hatali_secim_hakki)

            sesli_konus(
                f"Hatalı giriş yaptınız. "
                f"Kalan hakkınız {hatali_secim_hakki}."
            )

            if hatali_secim_hakki == 0:
                sistemi_kilitle()


mod_sec()
ana_menu()