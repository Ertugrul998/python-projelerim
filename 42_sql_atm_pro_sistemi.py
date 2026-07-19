import sqlite3
import hashlib
import getpass
from datetime import datetime


# --------------------------------------------------
# SABİTLER
# --------------------------------------------------

VERITABANI_ADI = "atm_pro.db"
MAKSIMUM_PIN_DENEMESI = 3


# --------------------------------------------------
# YARDIMCI FONKSİYONLAR
# --------------------------------------------------

def tarih_al():
    """Şu anki tarih ve saati metin olarak döndürür."""

    return datetime.now().strftime("%d.%m.%Y %H:%M:%S")


def pin_sifrele(pin):
    """PIN kodunu SHA-256 algoritmasıyla şifreler."""

    return hashlib.sha256(
        pin.encode("utf-8")
    ).hexdigest()


def para_formatla(miktar):
    """Para miktarını Türkçe para formatına dönüştürür."""

    return (
        f"{miktar:,.2f} TL"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def guvenli_pin_al(mesaj):
    """
    PIN girilirken karakterleri gizlemeye çalışır.
    PyCharm konsolunda getpass çalışmazsa normal input kullanılır.
    """

    try:
        return getpass.getpass(mesaj).strip()

    except (EOFError, OSError):
        return input(mesaj).strip()


# --------------------------------------------------
# VERİTABANI SINIFI
# --------------------------------------------------

class ATMVeritabani:

    def __init__(self):

        self.baglanti = sqlite3.connect(
            VERITABANI_ADI
        )

        self.baglanti.row_factory = sqlite3.Row
        self.imlec = self.baglanti.cursor()

        self.tablolari_olustur()
        self.ornek_kart_olustur()

    def tablolari_olustur(self):

        self.imlec.execute("""
            CREATE TABLE IF NOT EXISTS kartlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kart_numarasi TEXT UNIQUE NOT NULL,
                ad_soyad TEXT NOT NULL,
                pin_hash TEXT NOT NULL,
                bakiye REAL NOT NULL DEFAULT 0,
                hatali_pin INTEGER NOT NULL DEFAULT 0,
                bloke INTEGER NOT NULL DEFAULT 0,
                son_giris TEXT,
                olusturma_tarihi TEXT NOT NULL
            )
        """)

        self.imlec.execute("""
            CREATE TABLE IF NOT EXISTS islemler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kart_id INTEGER NOT NULL,
                islem_turu TEXT NOT NULL,
                miktar REAL NOT NULL DEFAULT 0,
                onceki_bakiye REAL NOT NULL,
                sonraki_bakiye REAL NOT NULL,
                aciklama TEXT,
                tarih TEXT NOT NULL,

                FOREIGN KEY (kart_id)
                REFERENCES kartlar(id)
            )
        """)

        self.baglanti.commit()

    def ornek_kart_olustur(self):

        kart_numarasi = "1234567890123456"

        self.imlec.execute("""
            SELECT id
            FROM kartlar
            WHERE kart_numarasi = ?
        """, (kart_numarasi,))

        kart = self.imlec.fetchone()

        if kart is None:

            self.imlec.execute("""
                INSERT INTO kartlar (
                    kart_numarasi,
                    ad_soyad,
                    pin_hash,
                    bakiye,
                    hatali_pin,
                    bloke,
                    son_giris,
                    olusturma_tarihi
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                kart_numarasi,
                "Ayaz Kullanıcı",
                pin_sifrele("2580"),
                10000.00,
                0,
                0,
                None,
                tarih_al()
            ))

            self.baglanti.commit()

    def kart_bul(self, kart_numarasi):

        self.imlec.execute("""
            SELECT *
            FROM kartlar
            WHERE kart_numarasi = ?
        """, (kart_numarasi,))

        return self.imlec.fetchone()

    @staticmethod
    def pin_dogrula(kart, girilen_pin):

        girilen_pin_hash = pin_sifrele(
            girilen_pin
        )

        return kart["pin_hash"] == girilen_pin_hash

    def hatali_pin_arttir(self, kart_id):

        self.imlec.execute("""
            UPDATE kartlar
            SET hatali_pin = hatali_pin + 1
            WHERE id = ?
        """, (kart_id,))

        self.baglanti.commit()

        self.imlec.execute("""
            SELECT hatali_pin
            FROM kartlar
            WHERE id = ?
        """, (kart_id,))

        sonuc = self.imlec.fetchone()

        return sonuc["hatali_pin"]

    def karti_bloke_et(self, kart_id):

        self.imlec.execute("""
            UPDATE kartlar
            SET bloke = 1
            WHERE id = ?
        """, (kart_id,))

        self.baglanti.commit()

    def basarili_giris_kaydet(self, kart_id):

        self.imlec.execute("""
            UPDATE kartlar
            SET
                hatali_pin = 0,
                son_giris = ?
            WHERE id = ?
        """, (
            tarih_al(),
            kart_id
        ))

        self.baglanti.commit()

    def bakiye_al(self, kart_id):

        self.imlec.execute("""
            SELECT bakiye
            FROM kartlar
            WHERE id = ?
        """, (kart_id,))

        sonuc = self.imlec.fetchone()

        if sonuc is None:
            raise ValueError(
                "Hesap bakiyesi bulunamadı."
            )

        return sonuc["bakiye"]

    def para_yatir(self, kart_id, miktar):

        onceki_bakiye = self.bakiye_al(
            kart_id
        )

        sonraki_bakiye = (
            onceki_bakiye + miktar
        )

        try:

            self.imlec.execute("""
                UPDATE kartlar
                SET bakiye = ?
                WHERE id = ?
            """, (
                sonraki_bakiye,
                kart_id
            ))

            self.islem_kaydet(
                kart_id=kart_id,
                islem_turu="PARA YATIRMA",
                miktar=miktar,
                onceki_bakiye=onceki_bakiye,
                sonraki_bakiye=sonraki_bakiye,
                aciklama=(
                    "ATM üzerinden para yatırıldı."
                )
            )

            self.baglanti.commit()

            return sonraki_bakiye

        except sqlite3.Error:
            self.baglanti.rollback()
            raise

    def para_cek(self, kart_id, miktar):

        onceki_bakiye = self.bakiye_al(
            kart_id
        )

        if miktar > onceki_bakiye:
            return False, onceki_bakiye

        sonraki_bakiye = (
            onceki_bakiye - miktar
        )

        try:

            self.imlec.execute("""
                UPDATE kartlar
                SET bakiye = ?
                WHERE id = ?
            """, (
                sonraki_bakiye,
                kart_id
            ))

            self.islem_kaydet(
                kart_id=kart_id,
                islem_turu="PARA ÇEKME",
                miktar=miktar,
                onceki_bakiye=onceki_bakiye,
                sonraki_bakiye=sonraki_bakiye,
                aciklama=(
                    "ATM üzerinden para çekildi."
                )
            )

            self.baglanti.commit()

            return True, sonraki_bakiye

        except sqlite3.Error:
            self.baglanti.rollback()
            raise

    def islem_kaydet(
        self,
        kart_id,
        islem_turu,
        miktar,
        onceki_bakiye,
        sonraki_bakiye,
        aciklama
    ):

        self.imlec.execute("""
            INSERT INTO islemler (
                kart_id,
                islem_turu,
                miktar,
                onceki_bakiye,
                sonraki_bakiye,
                aciklama,
                tarih
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            kart_id,
            islem_turu,
            miktar,
            onceki_bakiye,
            sonraki_bakiye,
            aciklama,
            tarih_al()
        ))

    def islem_gecmisi_al(
        self,
        kart_id,
        limit=10
    ):

        self.imlec.execute("""
            SELECT *
            FROM islemler
            WHERE kart_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (
            kart_id,
            limit
        ))

        return self.imlec.fetchall()

    def pin_degistir(
        self,
        kart_id,
        yeni_pin
    ):

        self.imlec.execute("""
            UPDATE kartlar
            SET pin_hash = ?
            WHERE id = ?
        """, (
            pin_sifrele(yeni_pin),
            kart_id
        ))

        self.baglanti.commit()

    def baglantiyi_kapat(self):

        if self.baglanti:

            self.baglanti.close()
            self.baglanti = None


# --------------------------------------------------
# ATM UYGULAMASI SINIFI
# --------------------------------------------------

class ATMPro:

    def __init__(self):

        self.veritabani = ATMVeritabani()
        self.aktif_kart = None

    def baslat(self):

        print("\n" + "=" * 50)
        print("              SQL ATM PRO")
        print("=" * 50)

        giris_basarili = self.giris_yap()

        if not giris_basarili:
            return

        self.ana_menu()

    def giris_yap(self):

        kart_numarasi = input(
            "\nKart numaranızı giriniz: "
        ).replace(" ", "").strip()

        if not kart_numarasi.isdigit():

            print(
                "\nKart numarası yalnızca "
                "rakamlardan oluşmalıdır."
            )

            return False

        if len(kart_numarasi) != 16:

            print(
                "\nKart numarası 16 haneli "
                "olmalıdır."
            )

            return False

        kart = self.veritabani.kart_bul(
            kart_numarasi
        )

        if kart is None:

            print(
                "\nBu kart numarasına ait "
                "hesap bulunamadı."
            )

            return False

        if kart["bloke"] == 1:

            print("\n" + "!" * 50)
            print("KARTINIZ BLOKE EDİLMİŞTİR.")
            print(
                "Lütfen bankanızla "
                "iletişime geçiniz."
            )
            print("!" * 50)

            return False

        kalan_hak = (
            MAKSIMUM_PIN_DENEMESI
            - kart["hatali_pin"]
        )

        while kalan_hak > 0:

            pin = guvenli_pin_al(
                "\nPIN kodunuzu giriniz: "
            )

            if (
                len(pin) == 4
                and pin.isdigit()
                and self.veritabani.pin_dogrula(
                    kart,
                    pin
                )
            ):

                onceki_giris = kart["son_giris"]

                self.veritabani.basarili_giris_kaydet(
                    kart["id"]
                )

                self.aktif_kart = (
                    self.veritabani.kart_bul(
                        kart_numarasi
                    )
                )

                print("\nGiriş başarılı.")
                print(
                    f"Hoş geldiniz, "
                    f"{kart['ad_soyad']}."
                )

                if onceki_giris:

                    print(
                        f"Önceki girişiniz: "
                        f"{onceki_giris}"
                    )

                else:

                    print(
                        "Bu hesabın ilk "
                        "başarılı girişidir."
                    )

                return True

            hatali_sayi = (
                self.veritabani.hatali_pin_arttir(
                    kart["id"]
                )
            )

            kalan_hak = (
                MAKSIMUM_PIN_DENEMESI
                - hatali_sayi
            )

            if kalan_hak > 0:

                print("\nPIN kodu yanlış.")

                print(
                    f"Kalan deneme hakkınız: "
                    f"{kalan_hak}"
                )

            else:

                self.veritabani.karti_bloke_et(
                    kart["id"]
                )

                print("\n" + "!" * 50)
                print(
                    "PIN KODU 3 KEZ "
                    "YANLIŞ GİRİLDİ."
                )
                print(
                    "KARTINIZ GÜVENLİK "
                    "NEDENİYLE BLOKE EDİLDİ."
                )
                print(
                    "Lütfen bankanızla "
                    "iletişime geçiniz."
                )
                print("!" * 50)

                return False

        return False

    def ana_menu(self):

        while True:

            print("\n" + "=" * 50)
            print("                 ANA MENÜ")
            print("=" * 50)
            print("1 - Bakiye görüntüle")
            print("2 - Para yatır")
            print("3 - Para çek")
            print("4 - İşlem geçmişi")
            print("5 - Son giriş bilgisi")
            print("6 - PIN değiştir")
            print("0 - Kartı çıkart")
            print("=" * 50)

            secim = input(
                "İşlem seçiniz: "
            ).strip()

            if secim == "1":
                self.bakiye_goster()

            elif secim == "2":
                self.para_yatir_menu()

            elif secim == "3":
                self.para_cek_menu()

            elif secim == "4":
                self.islem_gecmisi_goster()

            elif secim == "5":
                self.son_girisi_goster()

            elif secim == "6":
                self.pin_degistir_menu()

            elif secim == "0":

                print(
                    "\nKartınız çıkartılıyor..."
                )

                print(
                    "Bizi tercih ettiğiniz "
                    "için teşekkür ederiz."
                )

                break

            else:

                print(
                    "\nGeçersiz seçim yaptınız."
                )

    def bakiye_goster(self):

        bakiye = self.veritabani.bakiye_al(
            self.aktif_kart["id"]
        )

        print("\n" + "-" * 50)
        print(
            f"Güncel bakiyeniz: "
            f"{para_formatla(bakiye)}"
        )
        print("-" * 50)

    @staticmethod
    def miktar_al(mesaj):

        miktar_metni = input(
            mesaj
        ).strip()

        miktar_metni = miktar_metni.replace(
            ",",
            "."
        )

        try:

            miktar = float(miktar_metni)

        except ValueError:

            print(
                "\nGeçerli bir para "
                "miktarı giriniz."
            )

            return None

        if miktar <= 0:

            print(
                "\nMiktar sıfırdan "
                "büyük olmalıdır."
            )

            return None

        return round(miktar, 2)

    def para_yatir_menu(self):

        miktar = self.miktar_al(
            "\nYatırılacak miktar: "
        )

        if miktar is None:
            return

        yeni_bakiye = (
            self.veritabani.para_yatir(
                self.aktif_kart["id"],
                miktar
            )
        )

        print(
            "\nPara yatırma işlemi başarılı."
        )

        print(
            f"Yatırılan miktar: "
            f"{para_formatla(miktar)}"
        )

        print(
            f"Yeni bakiye: "
            f"{para_formatla(yeni_bakiye)}"
        )

    def para_cek_menu(self):

        miktar = self.miktar_al(
            "\nÇekilecek miktar: "
        )

        if miktar is None:
            return

        basarili, sonuc_bakiye = (
            self.veritabani.para_cek(
                self.aktif_kart["id"],
                miktar
            )
        )

        if not basarili:

            print("\nYetersiz bakiye.")

            print(
                f"Mevcut bakiyeniz: "
                f"{para_formatla(sonuc_bakiye)}"
            )

            return

        print(
            "\nPara çekme işlemi başarılı."
        )

        print(
            f"Çekilen miktar: "
            f"{para_formatla(miktar)}"
        )

        print(
            f"Kalan bakiye: "
            f"{para_formatla(sonuc_bakiye)}"
        )

    def islem_gecmisi_goster(self):

        islemler = (
            self.veritabani.islem_gecmisi_al(
                self.aktif_kart["id"],
                limit=10
            )
        )

        print("\n" + "=" * 70)
        print("                    SON 10 İŞLEM")
        print("=" * 70)

        if not islemler:

            print(
                "Henüz kayıtlı bir işlem "
                "bulunmamaktadır."
            )

            print("=" * 70)
            return

        for islem in islemler:

            print(
                f"\nİşlem numarası : "
                f"{islem['id']}"
            )

            print(
                f"İşlem türü     : "
                f"{islem['islem_turu']}"
            )

            print(
                f"Miktar         : "
                f"{para_formatla(islem['miktar'])}"
            )

            print(
                f"Önceki bakiye  : "
                f"{para_formatla(islem['onceki_bakiye'])}"
            )

            print(
                f"Sonraki bakiye : "
                f"{para_formatla(islem['sonraki_bakiye'])}"
            )

            print(
                f"Tarih          : "
                f"{islem['tarih']}"
            )

            print(
                f"Açıklama       : "
                f"{islem['aciklama']}"
            )

            print("-" * 70)

    def son_girisi_goster(self):

        kart = self.veritabani.kart_bul(
            self.aktif_kart["kart_numarasi"]
        )

        print("\n" + "-" * 50)

        if kart["son_giris"]:

            print(
                f"Son başarılı giriş: "
                f"{kart['son_giris']}"
            )

        else:

            print(
                "Son giriş bilgisi "
                "bulunmamaktadır."
            )

        print("-" * 50)

    def pin_degistir_menu(self):

        mevcut_pin = guvenli_pin_al(
            "\nMevcut PIN kodunuz: "
        )

        kart = self.veritabani.kart_bul(
            self.aktif_kart["kart_numarasi"]
        )

        if not self.veritabani.pin_dogrula(
            kart,
            mevcut_pin
        ):

            print(
                "\nMevcut PIN kodu yanlış."
            )

            return

        yeni_pin = guvenli_pin_al(
            "Yeni 4 haneli PIN kodunuz: "
        )

        if (
            not yeni_pin.isdigit()
            or len(yeni_pin) != 4
        ):

            print(
                "\nPIN kodu 4 rakamdan "
                "oluşmalıdır."
            )

            return

        yeni_pin_tekrar = guvenli_pin_al(
            "Yeni PIN kodunu tekrar giriniz: "
        )

        if yeni_pin != yeni_pin_tekrar:

            print(
                "\nGirilen yeni PIN kodları "
                "aynı değil."
            )

            return

        if yeni_pin == mevcut_pin:

            print(
                "\nYeni PIN eski PIN ile "
                "aynı olamaz."
            )

            return

        self.veritabani.pin_degistir(
            self.aktif_kart["id"],
            yeni_pin
        )

        print(
            "\nPIN kodunuz başarıyla "
            "değiştirildi."
        )


# --------------------------------------------------
# PROGRAMIN BAŞLANGIÇ NOKTASI
# --------------------------------------------------

def main():

    uygulama = None

    try:

        uygulama = ATMPro()
        uygulama.baslat()

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

    except ValueError as hata:

        print(
            "\nGeçersiz değer hatası oluştu:"
        )

        print(hata)

    finally:

        if uygulama is not None:

            uygulama.veritabani.baglantiyi_kapat()

        print("\nProgram kapatıldı.")


if __name__ == "__main__":
    main()


# --------------------------------------------------
# PROGRAM SONU
# --------------------------------------------------

