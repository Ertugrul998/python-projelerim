import sqlite3
from datetime import datetime


# --------------------------------------------------
# SABİTLER
# --------------------------------------------------

VERITABANI_ADI = "kutuphane_44.db"


# --------------------------------------------------
# YARDIMCI FONKSİYON
# --------------------------------------------------

def tarih_al():
    return datetime.now().strftime(
        "%d.%m.%Y %H:%M:%S"
    )


# --------------------------------------------------
# VERİTABANI SINIFI
# --------------------------------------------------

class KutuphaneVeritabani:

    def __init__(self):

        self.baglanti = sqlite3.connect(
            VERITABANI_ADI
        )

        self.imlec = self.baglanti.cursor()

        self.tablolari_olustur()

    def tablolari_olustur(self):

        self.imlec.execute("""
            CREATE TABLE IF NOT EXISTS kitaplar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kitap_adi TEXT NOT NULL,
                yazar TEXT NOT NULL,
                durum TEXT NOT NULL,
                eklenme_tarihi TEXT NOT NULL
            )
        """)

        self.imlec.execute("""
            CREATE TABLE IF NOT EXISTS gecmis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                islem TEXT NOT NULL,
                kitap TEXT NOT NULL,
                tarih TEXT NOT NULL
            )
        """)

        self.baglanti.commit()

    def gecmis_kaydet(
        self,
        islem_turu,
        kitap_adi
    ):

        self.imlec.execute("""
            INSERT INTO gecmis (
                islem,
                kitap,
                tarih
            )
            VALUES (?, ?, ?)
        """, (
            islem_turu,
            kitap_adi,
            tarih_al()
        ))

    def kitap_ekle(
        self,
        kitap_adi,
        yazar_adi
    ):

        self.imlec.execute("""
            INSERT INTO kitaplar (
                kitap_adi,
                yazar,
                durum,
                eklenme_tarihi
            )
            VALUES (?, ?, ?, ?)
        """, (
            kitap_adi,
            yazar_adi,
            "MUSAIT",
            tarih_al()
        ))

        self.gecmis_kaydet(
            "KITAP EKLENDI",
            kitap_adi
        )

        self.baglanti.commit()

    def kitaplari_listele(self):

        self.imlec.execute("""
            SELECT *
            FROM kitaplar
            ORDER BY id
        """)

        return self.imlec.fetchall()

    def kitap_ara(self, arama_metni):

        self.imlec.execute("""
            SELECT *
            FROM kitaplar
            WHERE kitap_adi LIKE ?
               OR yazar LIKE ?
            ORDER BY id
        """, (
            f"%{arama_metni}%",
            f"%{arama_metni}%"
        ))

        return self.imlec.fetchall()

    def kitap_sil(self, silinecek_id):

        self.imlec.execute("""
            SELECT kitap_adi
            FROM kitaplar
            WHERE id = ?
        """, (silinecek_id,))

        bulunan_kitap = self.imlec.fetchone()

        if bulunan_kitap is None:
            return False

        silinen_kitap_adi = bulunan_kitap[0]

        self.imlec.execute("""
            DELETE FROM kitaplar
            WHERE id = ?
        """, (silinecek_id,))

        self.gecmis_kaydet(
            "KITAP SILINDI",
            silinen_kitap_adi
        )

        self.baglanti.commit()

        return True

    def gecmisi_listele(self):

        self.imlec.execute("""
            SELECT *
            FROM gecmis
            ORDER BY id DESC
        """)

        return self.imlec.fetchall()

    def baglantiyi_kapat(self):

        if self.baglanti is not None:

            self.baglanti.close()
            self.baglanti = None


# --------------------------------------------------
# EKRANA YAZDIRMA FONKSİYONLARI
# --------------------------------------------------

def kitaplari_yazdir(kitaplar):

    if not kitaplar:

        print("\nKayıtlı kitap bulunamadı.")
        return

    print("\n" + "=" * 65)
    print("                     KİTAP LİSTESİ")
    print("=" * 65)

    for kayit in kitaplar:

        print(f"\nKitap ID      : {kayit[0]}")
        print(f"Kitap adı     : {kayit[1]}")
        print(f"Yazar         : {kayit[2]}")
        print(f"Durum         : {kayit[3]}")
        print(f"Eklenme tarihi: {kayit[4]}")
        print("-" * 65)


def gecmisi_yazdir(islemler):

    if not islemler:

        print("\nİşlem geçmişi bulunamadı.")
        return

    print("\n" + "=" * 65)
    print("                    İŞLEM GEÇMİŞİ")
    print("=" * 65)

    for kayit in islemler:

        print(f"\nİşlem ID   : {kayit[0]}")
        print(f"İşlem türü : {kayit[1]}")
        print(f"Kitap      : {kayit[2]}")
        print(f"Tarih      : {kayit[3]}")
        print("-" * 65)


# --------------------------------------------------
# ANA UYGULAMA
# --------------------------------------------------

def main():

    veritabani = KutuphaneVeritabani()

    try:

        while True:

            print("\n" + "=" * 50)
            print("          SQL KÜTÜPHANE PRO MAX")
            print("=" * 50)
            print("1 - Kitap ekle")
            print("2 - Kitapları listele")
            print("3 - Kitap ara")
            print("4 - Kitap sil")
            print("5 - İşlem geçmişi")
            print("0 - Programı kapat")
            print("=" * 50)

            secim = input(
                "Seçiminiz: "
            ).strip()

            if secim == "1":

                kitap_adi = input(
                    "\nKitap adı: "
                ).strip()

                yazar_adi = input(
                    "Yazar adı: "
                ).strip()

                if not kitap_adi:

                    print(
                        "\nKitap adı boş bırakılamaz."
                    )

                    continue

                if not yazar_adi:

                    print(
                        "\nYazar adı boş bırakılamaz."
                    )

                    continue

                veritabani.kitap_ekle(
                    kitap_adi,
                    yazar_adi
                )

                print(
                    "\nKitap başarıyla eklendi."
                )

            elif secim == "2":

                kitap_listesi = (
                    veritabani.kitaplari_listele()
                )

                kitaplari_yazdir(
                    kitap_listesi
                )

            elif secim == "3":

                arama_metni = input(
                    "\nKitap veya yazar adı: "
                ).strip()

                if not arama_metni:

                    print(
                        "\nArama metni boş bırakılamaz."
                    )

                    continue

                arama_sonuclari = (
                    veritabani.kitap_ara(
                        arama_metni
                    )
                )

                kitaplari_yazdir(
                    arama_sonuclari
                )

            elif secim == "4":

                try:

                    silinecek_id = int(
                        input(
                            "\nSilinecek kitap ID: "
                        )
                    )

                except ValueError:

                    print(
                        "\nKitap ID sayı olmalıdır."
                    )

                    continue

                silme_basarili = (
                    veritabani.kitap_sil(
                        silinecek_id
                    )
                )

                if silme_basarili:

                    print(
                        "\nKitap başarıyla silindi."
                    )

                else:

                    print(
                        "\nBu ID numarasıyla "
                        "kitap bulunamadı."
                    )

            elif secim == "5":

                islem_listesi = (
                    veritabani.gecmisi_listele()
                )

                gecmisi_yazdir(
                    islem_listesi
                )

            elif secim == "0":

                print(
                    "\nProgram kapatılıyor..."
                )

                break

            else:

                print(
                    "\nGeçersiz menü seçimi."
                )

    except KeyboardInterrupt:

        print(
            "\n\nProgram kullanıcı "
            "tarafından kapatıldı."
        )

    except sqlite3.Error as hata:

        print(
            "\nVeritabanı hatası oluştu:"
        )

        print(hata)

    finally:

        veritabani.baglantiyi_kapat()

        print(
            "\nVeritabanı bağlantısı kapatıldı."
        )


# --------------------------------------------------
# PROGRAMIN BAŞLANGIÇ NOKTASI
# --------------------------------------------------

if __name__ == "__main__":
    main()


# --------------------------------------------------
# PROGRAM SONU
# --------------------------------------------------