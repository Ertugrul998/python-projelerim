import json
import os
from datetime import datetime
from pathlib import Path

def seslendir(metin):
    os.system(f'say "{metin}"')

DOSYA_ADI = Path("notlar.json")


def notlari_yukle():
    if not DOSYA_ADI.exists():
        return []

    try:
        with DOSYA_ADI.open("r", encoding="utf-8") as dosya:
            return json.load(dosya)
    except (json.JSONDecodeError, OSError):
        print("Not dosyası okunamadı. Boş listeyle devam ediliyor.")
        return []


def notlari_kaydet(notlar):
    try:
        with DOSYA_ADI.open("w", encoding="utf-8") as dosya:
            json.dump(notlar, dosya, ensure_ascii=False, indent=4)
    except OSError:
        print("Notlar kaydedilemedi.")


def not_ekle(notlar):
    baslik = input("Not başlığı: ").strip()
    icerik = input("Not içeriği: ").strip()

    if not baslik or not icerik:
        print("Başlık ve içerik boş bırakılamaz.")
        return

    yeni_not = {
        "id": max((not_["id"] for not_ in notlar), default=0) + 1,
        "baslik": baslik,
        "icerik": icerik,
        "tarih": datetime.now().strftime("%d.%m.%Y %H:%M")
    }

    notlar.append(yeni_not)
    notlari_kaydet(notlar)
    print("Not başarıyla eklendi.")
    seslendir("Not başarıyla eklendi")


def notlari_goster(notlar):
    if not notlar:
        print("Kayıtlı not bulunmuyor.")
        return

    print("\n--- KAYITLI NOTLAR ---")

    for not_ in notlar:
        print(f"\nID: {not_['id']}")
        print(f"Başlık: {not_['baslik']}")
        print(f"İçerik: {not_['icerik']}")
        print(f"Tarih: {not_['tarih']}")
        print("-" * 30)


def not_ara(notlar):
    aranan = input("Aranacak kelime: ").strip().lower()

    bulunanlar = [
        not_ for not_ in notlar
        if aranan in not_["baslik"].lower()
        or aranan in not_["icerik"].lower()
    ]

    if not bulunanlar:
        print("Aramaya uygun not bulunamadı.")
        return

    notlari_goster(bulunanlar)


def not_guncelle(notlar):
    notlari_goster(notlar)

    try:
        not_id = int(input("Güncellenecek notun ID numarası: "))
    except ValueError:
        print("Geçerli bir sayı gir.")
        return

    for not_ in notlar:
        if not_["id"] == not_id:
            yeni_baslik = input(
                f"Yeni başlık [{not_['baslik']}]: "
            ).strip()

            yeni_icerik = input(
                f"Yeni içerik [{not_['icerik']}]: "
            ).strip()

            if yeni_baslik:
                not_["baslik"] = yeni_baslik

            if yeni_icerik:
                not_["icerik"] = yeni_icerik

            not_["tarih"] = datetime.now().strftime("%d.%m.%Y %H:%M")

            notlari_kaydet(notlar)
            print("Not güncellendi.")
            seslendir("Not güncellendi")
            return

    print("Bu ID numarasına ait not bulunamadı.")


def not_sil(notlar):
    notlari_goster(notlar)

    try:
        not_id = int(input("Silinecek notun ID numarası: "))
    except ValueError:
        print("Geçerli bir sayı gir.")
        return

    for not_ in notlar:
        if not_["id"] == not_id:
            onay = input(
                f"'{not_['baslik']}' silinsin mi? (e/h): "
            ).strip().lower()

            if onay == "e":
                notlar.remove(not_)
                notlari_kaydet(notlar)
                print("Not silindi.")
                seslendir("Not silindi")
            else:
                print("Silme işlemi iptal edildi.")

            return

    print("Bu ID numarasına ait not bulunamadı.")


def menu():
    notlar = notlari_yukle()
    seslendir("Not yönetim sistemine hoş geldiniz")

    while True:
        print("""
========= NOT YÖNETİM SİSTEMİ =========
1- Not Ekle
2- Notları Göster
3- Not Ara
4- Not Güncelle
5- Not Sil
6- Çıkış
========================================
""")

        secim = input("Seçimin: ").strip()

        if secim == "1":
            not_ekle(notlar)

        elif secim == "2":
            notlari_goster(notlar)

        elif secim == "3":
            not_ara(notlar)

        elif secim == "4":
            not_guncelle(notlar)

        elif secim == "5":
            not_sil(notlar)

        elif secim == "6":
            print("Notlar kaydedildi. Program kapatılıyor.")
            seslendir("Görüşmek üzere Ertuğrul")
            break

        else:
            print("Geçersiz seçim. 1 ile 6 arasında seçim yap.")


if __name__ == "__main__":
    menu()