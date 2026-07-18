# Proje 26 - Görev Takip Sistemi

import subprocess

GOREV_DOSYASI = "gorevler.txt"


def sesli_konus(metin):
    subprocess.run(["say", metin], check=False)


def gorevleri_oku():
    try:
        with open(GOREV_DOSYASI, "r", encoding="utf-8") as dosya:
            return [satir.strip() for satir in dosya if satir.strip()]
    except FileNotFoundError:
        return []


def gorevleri_kaydet(gorevler):
    with open(GOREV_DOSYASI, "w", encoding="utf-8") as dosya:
        for gorev in gorevler:
            dosya.write(gorev + "\n")


def gorev_ekle():
    gorev = input("Yeni görevi yazınız: ").strip()

    if not gorev:
        print("❌ Boş görev eklenemez.")
        return

    with open(GOREV_DOSYASI, "a", encoding="utf-8") as dosya:
        dosya.write("[BEKLİYOR] " + gorev + "\n")

    print("✅ Görev eklendi.")
    sesli_konus("Görev başarıyla eklendi.")


def gorevleri_goster():
    gorevler = gorevleri_oku()

    if not gorevler:
        print("📭 Kayıtlı görev bulunamadı.")
        return

    print("\n===== GÖREVLER =====")

    for numara, gorev in enumerate(gorevler, start=1):
        print(f"{numara} - {gorev}")


def gorevi_tamamla():
    gorevler = gorevleri_oku()
    gorevleri_goster()

    if not gorevler:
        return

    try:
        secim = int(input("Tamamlanan görev numarası: "))

        if secim < 1 or secim > len(gorevler):
            print("❌ Geçersiz görev numarası.")
            return

        gorev = gorevler[secim - 1]
        gorev = gorev.replace("[BEKLİYOR]", "[TAMAMLANDI]")
        gorevler[secim - 1] = gorev

        gorevleri_kaydet(gorevler)

        print("✅ Görev tamamlandı.")
        sesli_konus("Görev tamamlandı.")

    except ValueError:
        print("❌ Yalnızca sayı giriniz.")


def gorev_sil():
    gorevler = gorevleri_oku()
    gorevleri_goster()

    if not gorevler:
        return

    try:
        secim = int(input("Silinecek görev numarası: "))

        if secim < 1 or secim > len(gorevler):
            print("❌ Geçersiz görev numarası.")
            return

        silinen = gorevler.pop(secim - 1)
        gorevleri_kaydet(gorevler)

        print("🗑️ Silinen görev:", silinen)

    except ValueError:
        print("❌ Yalnızca sayı giriniz.")


while True:
    print("\n===== GÖREV TAKİP SİSTEMİ =====")
    print("1 - Görev ekle")
    print("2 - Görevleri göster")
    print("3 - Görevi tamamla")
    print("4 - Görev sil")
    print("5 - Çıkış")

    secim = input("Seçiminiz: ").strip()

    if secim == "1":
        gorev_ekle()
    elif secim == "2":
        gorevleri_goster()
    elif secim == "3":
        gorevi_tamamla()
    elif secim == "4":
        gorev_sil()
    elif secim == "5":
        print("Program kapatılıyor.")
        break
    else:
        print("❌ Geçersiz seçim.")