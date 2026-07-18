# Proje 31.1 - Alarmlı Sesli Hesap Makinesi
# Sürüm 1.0

import subprocess
import sys
import threading
import time


ALARM_DOSYASI = "/System/Library/Sounds/Sosumi.aiff"
sesli_mod = False


def sesli_konus(metin):
    """Sesli mod açıksa Mac'in say komutuyla konuşur."""
    if sesli_mod:
        subprocess.run(
            ["say", metin],
            check=False
        )


def mod_sec():
    """Programın sesli veya sessiz çalışmasını seçtirir."""
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


def alarm_sesi(durdurma_sinyali):
    """Enter tuşuna basılıncaya kadar alarm çalar."""
    while not durdurma_sinyali.is_set():
        subprocess.run(
            ["afplay", ALARM_DOSYASI],
            check=False
        )

        time.sleep(0.2)


def sistemi_kilitle():
    """Üç yanlış seçimden sonra alarmı başlatır ve programı kapatır."""
    print("\n🚨 Üç kez hatalı seçim yapıldı!")
    print("🔒 Hesap makinesi kilitlendi.")
    print("⏎ Alarmı durdurmak için Enter tuşuna basınız.")

    sesli_konus(
        "Dikkat. Üç kez hatalı seçim yapıldı. "
        "Hesap makinesi kilitlendi. "
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


def sayi_al(mesaj):
    """Kullanıcıdan geçerli bir sayı alır."""
    try:
        sayi_metni = input(mesaj).strip().replace(",", ".")
        return float(sayi_metni)

    except ValueError:
        print("❌ Lütfen geçerli bir sayı giriniz.")
        sesli_konus("Lütfen geçerli bir sayı giriniz.")
        return None


def islemi_yap(secim):
    """Seçilen matematik işlemini gerçekleştirir."""
    sayi1 = sayi_al("1. sayı: ")

    if sayi1 is None:
        return

    sayi2 = sayi_al("2. sayı: ")

    if sayi2 is None:
        return

    if secim == "1":
        sonuc = sayi1 + sayi2
        islem_adi = "Toplama"

    elif secim == "2":
        sonuc = sayi1 - sayi2
        islem_adi = "Çıkarma"

    elif secim == "3":
        sonuc = sayi1 * sayi2
        islem_adi = "Çarpma"

    elif secim == "4":
        if sayi2 == 0:
            print("❌ Bir sayı sıfıra bölünemez.")
            sesli_konus("Bir sayı sıfıra bölünemez.")
            return

        sonuc = sayi1 / sayi2
        islem_adi = "Bölme"

    else:
        sonuc = sayi1 ** sayi2
        islem_adi = "Üs alma"

    print("\n========================")
    print(f"İşlem : {islem_adi}")
    print(f"Sonuç : {sonuc}")
    print("========================")

    sesli_konus(
        f"{islem_adi} işleminin sonucu {sonuc}"
    )


def ana_menu():
    """Hesap makinesinin ana menüsünü çalıştırır."""
    hatali_secim_hakki = 3

    sesli_konus(
        "Alarmlı hesap makinesine hoş geldiniz."
    )

    while True:
        print("\n========================")
        print("  ALARMLI HESAP MAKİNESİ")
        print("========================")
        print("1 - Toplama")
        print("2 - Çıkarma")
        print("3 - Çarpma")
        print("4 - Bölme")
        print("5 - Üs alma")
        print("6 - Ses modunu değiştir")
        print("7 - Çıkış")

        sesli_konus("Bir işlem seçiniz.")

        secim = input("Seçiminiz: ").strip()

        if secim in ["1", "2", "3", "4", "5"]:
            islemi_yap(secim)

            # Geçerli bir menü seçimi yapıldığında hak yenilenir.
            hatali_secim_hakki = 3

        elif secim == "6":
            mod_sec()
            hatali_secim_hakki = 3

        elif secim == "7":
            print("\n✅ Çıkış yapıldı.")
            sesli_konus("Çıkış yapıldı.")
            break

        else:
            hatali_secim_hakki -= 1

            print("\n❌ Hatalı giriş yaptınız.")
            print(
                "Kalan hatalı seçim hakkı:",
                hatali_secim_hakki
            )

            sesli_konus(
                f"Hatalı giriş yaptınız. "
                f"Kalan hakkınız {hatali_secim_hakki}."
            )

            if hatali_secim_hakki == 0:
                sistemi_kilitle()


mod_sec()
ana_menu()