import getpass
import json
import subprocess
from datetime import datetime
from pathlib import Path


SIFRE = "2580"
DOSYA_ADI = Path("notlar.json")


def seslendir(metin):
    """macOS üzerinde verilen metni seslendirir."""
    subprocess.run(["say", metin], check=False)


def sifre_dogrula(mesaj="Şifreyi gir: "):
    """Şifreyi görünmeden alır ve doğru olup olmadığını döndürür."""
    girilen_sifre = getpass.getpass(mesaj)

    if girilen_sifre == SIFRE:
        print("Şifre doğru.")
        seslendir("Şifre doğru")
        return True

    print("Şifre yanlış!")
    seslendir("Şifre yanlış")
    return False


def notlari_yukle():
    """JSON dosyasındaki notları yükler."""
    if not DOSYA_ADI.exists():
        return []

    try:
        with DOSYA_ADI.open("r", encoding="utf-8") as dosya:
            veriler = json.load(dosya)

            if isinstance(veriler, list):
                return veriler

            print("Not dosyasının yapısı geçersiz.")
            return []

    except (json.JSONDecodeError, OSError):
        print("Not dosyası okunamadı. Boş listeyle devam ediliyor.")
        seslendir("Not dosyası okunamadı")
        return []


def notlari_kaydet(notlar):
    """Notları JSON dosyasına kaydeder."""
    try:
        with DOSYA_ADI.open("w", encoding="utf-8") as dosya:
            json.dump(notlar, dosya, ensure_ascii=False, indent=4)

        return True

    except OSError:
        print("Notlar kaydedilemedi.")
        seslendir("Notlar kaydedilemedi")
        return False


def not_ekle(notlar):
    """Şifre doğrulandıktan sonra yeni not ekler."""
    if not sifre_dogrula("Not eklemek için şifreyi gir: "):
        return

    baslik = input("Not başlığı: ").strip()
    icerik = input("Not içeriği: ").strip()

    if not baslik or not icerik:
        print("Başlık ve içerik boş bırakılamaz.")
        seslendir("Başlık ve içerik boş bırakılamaz")
        return

    yeni_not = {
        "id": max((not_["id"] for not_ in notlar), default=0) + 1,
        "baslik": baslik,
        "icerik": icerik,
        "tarih": datetime.now().strftime("%d.%m.%Y %H:%M"),
    }

    notlar.append(yeni_not)

    if notlari_kaydet(notlar):
        print("Not başarıyla eklendi.")
        seslendir("Not başarıyla eklendi")


def notlari_yazdir(notlar):
    """Notları şifre sormadan ekrana yazdıran yardımcı fonksiyon."""
    if not notlar:
        print("Kayıtlı not bulunmuyor.")
        seslendir("Kayıtlı not bulunmuyor")
        return

    print("\n========= KAYITLI NOTLAR =========")

    for not_ in notlar:
        print(f"\nID: {not_['id']}")
        print(f"Başlık: {not_['baslik']}")
        print(f"İçerik: {not_['icerik']}")
        print(f"Tarih: {not_['tarih']}")
        print("-" * 35)


def notlari_goster(notlar):
    """Şifre doğrulandıktan sonra bütün notları gösterir."""
    if not sifre_dogrula("Notları görüntülemek için şifreyi gir: "):
        return

    notlari_yazdir(notlar)


def not_ara(notlar):
    """Şifre doğrulandıktan sonra notlarda arama yapar."""
    if not sifre_dogrula("Not aramak için şifreyi gir: "):
        return

    aranan = input("Aranacak kelime: ").strip().lower()

    if not aranan:
        print("Arama kelimesi boş bırakılamaz.")
        return

    bulunanlar = [
        not_
        for not_ in notlar
        if aranan in not_["baslik"].lower()
        or aranan in not_["icerik"].lower()
    ]

    if not bulunanlar:
        print("Aramaya uygun not bulunamadı.")
        seslendir("Aramaya uygun not bulunamadı")
        return

    notlari_yazdir(bulunanlar)


def not_guncelle(notlar):
    """Şifre doğrulandıktan sonra seçilen notu günceller."""
    if not sifre_dogrula("Not güncellemek için şifreyi gir: "):
        return

    if not notlar:
        print("Güncellenecek not bulunmuyor.")
        return

    notlari_yazdir(notlar)

    try:
        not_id = int(input("Güncellenecek notun ID numarası: "))
    except ValueError:
        print("Geçerli bir sayı gir.")
        seslendir("Geçerli bir sayı gir")
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

            not_["tarih"] = datetime.now().strftime(
                "%d.%m.%Y %H:%M"
            )

            if notlari_kaydet(notlar):
                print("Not başarıyla güncellendi.")
                seslendir("Not başarıyla güncellendi")

            return

    print("Bu ID numarasına ait not bulunamadı.")
    seslendir("Not bulunamadı")


def not_sil(notlar):
    """Şifre doğrulandıktan sonra seçilen notu siler."""
    if not sifre_dogrula("Not silmek için şifreyi gir: "):
        return

    if not notlar:
        print("Silinecek not bulunmuyor.")
        return

    notlari_yazdir(notlar)

    try:
        not_id = int(input("Silinecek notun ID numarası: "))
    except ValueError:
        print("Geçerli bir sayı gir.")
        seslendir("Geçerli bir sayı gir")
        return

    for not_ in notlar:
        if not_["id"] == not_id:
            onay = input(
                f"'{not_['baslik']}' silinsin mi? (e/h): "
            ).strip().lower()

            if onay == "e":
                notlar.remove(not_)

                if notlari_kaydet(notlar):
                    print("Not başarıyla silindi.")
                    seslendir("Not başarıyla silindi")
            else:
                print("Silme işlemi iptal edildi.")
                seslendir("Silme işlemi iptal edildi")

            return

    print("Bu ID numarasına ait not bulunamadı.")
    seslendir("Not bulunamadı")


def menu():
    """Programın ana menüsünü çalıştırır."""
    print("========= ŞİFRELİ NOT KASASI =========")

    if not sifre_dogrula("Sisteme giriş şifresini gir: "):
        print("Sisteme giriş reddedildi.")
        seslendir("Sisteme giriş reddedildi")
        return

    notlar = notlari_yukle()

    print("Giriş başarılı. Sistem açılıyor.")
    seslendir("Şifreli not yönetim sistemine hoş geldiniz")

    while True:
        print(
            """
========= ŞİFRELİ NOT YÖNETİM SİSTEMİ =========
1- Not Ekle
2- Notları Göster
3- Not Ara
4- Not Güncelle
5- Not Sil
6- Çıkış
=================================================
"""
        )

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
            seslendir("Geçersiz seçim")


if __name__ == "__main__":
    menu()