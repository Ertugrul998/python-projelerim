gorevler = []


def gorev_ekle():
    gorev = input("Yeni görev: ")

    if gorev.strip() == "":
        print("Boş görev eklenemez.")
    else:
        gorevler.append({
            "gorev": gorev,
            "tamamlandi": False
        })

        print("Görev eklendi.")


def gorevleri_goster():
    if len(gorevler) == 0:
        print("Henüz görev yok.")
        return

    print("\n--- GÖREVLER ---")

    for sira, gorev_bilgisi in enumerate(gorevler, start=1):

        if gorev_bilgisi["tamamlandi"]:
            durum = "Tamamlandı"
        else:
            durum = "Bekliyor"

        print(
            sira,
            "-",
            gorev_bilgisi["gorev"],
            "-",
            durum
        )


def gorev_tamamla():
    gorevleri_goster()

    if len(gorevler) == 0:
        return

    try:
        numara = int(input("Tamamlanan görev numarası: "))

        if 1 <= numara <= len(gorevler):
            gorevler[numara - 1]["tamamlandi"] = True
            print("Görev tamamlandı olarak işaretlendi.")
        else:
            print("Geçersiz görev numarası.")

    except ValueError:
        print("Lütfen sayı gir.")


def gorev_sil():
    gorevleri_goster()

    if len(gorevler) == 0:
        return

    try:
        numara = int(input("Silinecek görev numarası: "))

        if 1 <= numara <= len(gorevler):
            silinen = gorevler.pop(numara - 1)
            print("Silinen görev:", silinen["gorev"])
        else:
            print("Geçersiz görev numarası.")

    except ValueError:
        print("Lütfen sayı gir.")


while True:

    print("\n--- GÖREV TAKİP SİSTEMİ ---")
    print("1 - Görev ekle")
    print("2 - Görevleri göster")
    print("3 - Görevi tamamla")
    print("4 - Görev sil")
    print("5 - Çıkış")

    secim = input("Seçiminiz: ")

    if secim == "1":
        gorev_ekle()

    elif secim == "2":
        gorevleri_goster()

    elif secim == "3":
        gorev_tamamla()

    elif secim == "4":
        gorev_sil()

    elif secim == "5":
        print("Program kapatıldı.")
        break

    else:
        print("Geçersiz seçim.")