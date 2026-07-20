import json
import os
import subprocess
import getpass
import sys

from datetime import datetime


# --------------------------------------------------
# SABİTLER
# --------------------------------------------------

STOK_DOSYASI = "stoklar_47.json"
GECMIS_DOSYASI = "stok_gecmis_47.json"

YONETICI_SIFRESI = "2580"
KRITIK_STOK_SEVIYESI = 5


# --------------------------------------------------
# YARDIMCI FONKSİYONLAR
# --------------------------------------------------

def tarih_al():

    return datetime.now().strftime(
        "%d.%m.%Y %H:%M:%S"
    )


def seslendir(metin):

    try:

        subprocess.run(
            ["say", str(metin)],
            check=False
        )

    except (FileNotFoundError, OSError):
        pass


def alarm_cal():

    try:

        subprocess.run(
            [
                "afplay",
                "/System/Library/Sounds/Sosumi.aiff"
            ],
            check=False
        )

    except (FileNotFoundError, OSError):
        pass


def mesaj_yaz(metin, sesli=True):

    print(metin)

    if sesli:
        seslendir(metin)


def guvenli_sifre_al(mesaj):

    try:

        return getpass.getpass(
            mesaj
        ).strip()

    except (EOFError, OSError):

        return input(
            mesaj
        ).strip()


def sistemi_kapat(mesaj, alarm=False):

    print("\n" + "!" * 60)
    print(mesaj)
    print("Sistem güvenlik nedeniyle kapatılıyor.")
    print("!" * 60)

    if alarm:
        alarm_cal()

    seslendir(mesaj)

    seslendir(
        "Sistem güvenlik nedeniyle kapatılıyor."
    )

    raise SystemExit


def yonetici_sifresi_dogrula():

    sifre = guvenli_sifre_al(
        "\nYönetici şifresini giriniz: "
    )

    if sifre == YONETICI_SIFRESI:

        mesaj_yaz(
            "\nŞifre doğru. Yetki verildi."
        )

        return

    sistemi_kapat(
        "Yanlış yönetici şifresi girildi.",
        alarm=True
    )


def para_formatla(miktar):

    return (
        f"{miktar:,.2f} TL"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


# --------------------------------------------------
# JSON DOSYA YÖNETİCİSİ
# --------------------------------------------------

class JSONDosyaYoneticisi:

    @staticmethod
    def dosyadan_oku(
        dosya_adi,
        varsayilan_veri
    ):

        if not os.path.exists(dosya_adi):

            return varsayilan_veri

        try:

            with open(
                dosya_adi,
                "r",
                encoding="utf-8"
            ) as dosya:

                return json.load(dosya)

        except json.JSONDecodeError:

            sistemi_kapat(
                f"{dosya_adi} dosyası bozulmuş.",
                alarm=True
            )

        except OSError as hata:

            sistemi_kapat(
                f"Dosya okunamadı. {hata}"
            )

        return varsayilan_veri

    @staticmethod
    def dosyaya_yaz(
        dosya_adi,
        veri
    ):

        gecici_dosya = (
            dosya_adi + ".tmp"
        )

        try:

            with open(
                gecici_dosya,
                "w",
                encoding="utf-8"
            ) as dosya:

                json.dump(
                    veri,
                    dosya,
                    ensure_ascii=False,
                    indent=4
                )

            os.replace(
                gecici_dosya,
                dosya_adi
            )

        except OSError as hata:

            try:

                if os.path.exists(
                    gecici_dosya
                ):

                    os.remove(
                        gecici_dosya
                    )

            except OSError:
                pass

            sistemi_kapat(
                f"Dosya kaydedilemedi. {hata}"
            )


# --------------------------------------------------
# STOK YÖNETİM SINIFI
# --------------------------------------------------

class StokYonetimSistemi:

    def __init__(self):

        self.urunler = (
            JSONDosyaYoneticisi.dosyadan_oku(
                STOK_DOSYASI,
                []
            )
        )

        self.gecmis = (
            JSONDosyaYoneticisi.dosyadan_oku(
                GECMIS_DOSYASI,
                []
            )
        )

    def verileri_kaydet(self):

        JSONDosyaYoneticisi.dosyaya_yaz(
            STOK_DOSYASI,
            self.urunler
        )

        JSONDosyaYoneticisi.dosyaya_yaz(
            GECMIS_DOSYASI,
            self.gecmis
        )

    def yeni_urun_id_al(self):

        if not self.urunler:
            return 1

        return max(
            urun["id"]
            for urun in self.urunler
        ) + 1

    def yeni_gecmis_id_al(self):

        if not self.gecmis:
            return 1

        return max(
            kayit["id"]
            for kayit in self.gecmis
        ) + 1

    def gecmis_kaydet(
        self,
        islem_turu,
        aciklama
    ):

        yeni_kayit = {
            "id": self.yeni_gecmis_id_al(),
            "islem_turu": islem_turu,
            "aciklama": aciklama,
            "tarih": tarih_al()
        }

        self.gecmis.append(
            yeni_kayit
        )

    def urun_bul(self, urun_id):

        for urun in self.urunler:

            if urun["id"] == urun_id:
                return urun

        return None

    def urun_ekle(
        self,
        urun_adi,
        kategori,
        adet,
        birim_fiyat
    ):

        yeni_urun = {
            "id": self.yeni_urun_id_al(),
            "urun_adi": urun_adi,
            "kategori": kategori,
            "adet": adet,
            "birim_fiyat": birim_fiyat,
            "kayit_tarihi": tarih_al(),
            "guncelleme_tarihi": None
        }

        self.urunler.append(
            yeni_urun
        )

        self.gecmis_kaydet(
            "ÜRÜN EKLENDİ",
            (
                f"{urun_adi} adlı ürün "
                f"{adet} adet olarak eklendi."
            )
        )

        self.verileri_kaydet()

        return yeni_urun["id"]

    def urunleri_listele(self):

        return self.urunler

    def urun_ara(self, arama_metni):

        arama_metni = (
            arama_metni.lower()
        )

        sonuclar = []

        for urun in self.urunler:

            bilgiler = (
                f"{urun['urun_adi']} "
                f"{urun['kategori']}"
            ).lower()

            if arama_metni in bilgiler:

                sonuclar.append(
                    urun
                )

        return sonuclar

    def stok_arttir(
        self,
        urun_id,
        miktar
    ):

        urun = self.urun_bul(
            urun_id
        )

        if urun is None:

            return (
                False,
                "Ürün bulunamadı."
            )

        urun["adet"] += miktar
        urun["guncelleme_tarihi"] = tarih_al()

        self.gecmis_kaydet(
            "STOK ARTIRILDI",
            (
                f"{urun['urun_adi']} adlı "
                f"ürünün stoğu {miktar} adet artırıldı."
            )
        )

        self.verileri_kaydet()

        return (
            True,
            "Stok başarıyla artırıldı."
        )

    def stok_azalt(
        self,
        urun_id,
        miktar
    ):

        urun = self.urun_bul(
            urun_id
        )

        if urun is None:

            return (
                False,
                "Ürün bulunamadı."
            )

        if miktar > urun["adet"]:

            sistemi_kapat(
                "Stok miktarından fazla ürün çıkarılamaz.",
                alarm=True
            )

        urun["adet"] -= miktar
        urun["guncelleme_tarihi"] = tarih_al()

        self.gecmis_kaydet(
            "STOK AZALTILDI",
            (
                f"{urun['urun_adi']} adlı "
                f"ürünün stoğu {miktar} adet azaltıldı."
            )
        )

        self.verileri_kaydet()

        return (
            True,
            "Stok başarıyla azaltıldı."
        )

    def fiyat_guncelle(
        self,
        urun_id,
        yeni_fiyat
    ):

        urun = self.urun_bul(
            urun_id
        )

        if urun is None:

            return (
                False,
                "Ürün bulunamadı."
            )

        eski_fiyat = urun[
            "birim_fiyat"
        ]

        urun["birim_fiyat"] = yeni_fiyat
        urun["guncelleme_tarihi"] = tarih_al()

        self.gecmis_kaydet(
            "FİYAT GÜNCELLENDİ",
            (
                f"{urun['urun_adi']} ürününün fiyatı "
                f"{para_formatla(eski_fiyat)} "
                f"tutarından "
                f"{para_formatla(yeni_fiyat)} "
                "tutarına güncellendi."
            )
        )

        self.verileri_kaydet()

        return (
            True,
            "Ürün fiyatı güncellendi."
        )

    def urun_sil(
        self,
        urun_id
    ):

        urun = self.urun_bul(
            urun_id
        )

        if urun is None:

            return (
                False,
                "Ürün bulunamadı."
            )

        urun_adi = urun[
            "urun_adi"
        ]

        self.urunler.remove(
            urun
        )

        self.gecmis_kaydet(
            "ÜRÜN SİLİNDİ",
            (
                f"{urun_adi} adlı ürün "
                "sistemden silindi."
            )
        )

        self.verileri_kaydet()

        return (
            True,
            "Ürün başarıyla silindi."
        )

    def kritik_stoklari_getir(self):

        return [
            urun
            for urun in self.urunler
            if urun["adet"] <= KRITIK_STOK_SEVIYESI
        ]

    def toplam_stok_degeri(self):

        return sum(
            urun["adet"]
            * urun["birim_fiyat"]
            for urun in self.urunler
        )

    def islem_gecmisini_getir(
        self,
        limit=30
    ):

        return list(
            reversed(
                self.gecmis[-limit:]
            )
        )


# --------------------------------------------------
# EKRANA YAZDIRMA FONKSİYONLARI
# --------------------------------------------------

def urunleri_yazdir(
    urunler,
    baslik
):

    if not urunler:

        mesaj_yaz(
            "\nÜrün kaydı bulunamadı."
        )

        return

    print("\n" + "=" * 80)
    print(f"{baslik:^80}")
    print("=" * 80)

    for urun in urunler:

        stok_degeri = (
            urun["adet"]
            * urun["birim_fiyat"]
        )

        print(
            f"\nÜrün ID          : {urun['id']}"
        )

        print(
            f"Ürün adı         : {urun['urun_adi']}"
        )

        print(
            f"Kategori         : {urun['kategori']}"
        )

        print(
            f"Stok adedi       : {urun['adet']}"
        )

        print(
            f"Birim fiyat      : "
            f"{para_formatla(urun['birim_fiyat'])}"
        )

        print(
            f"Toplam değer     : "
            f"{para_formatla(stok_degeri)}"
        )

        print(
            f"Kayıt tarihi     : "
            f"{urun['kayit_tarihi']}"
        )

        print(
            f"Güncelleme tarihi: "
            f"{urun['guncelleme_tarihi'] or '-'}"
        )

        print("-" * 80)

    seslendir(
        f"Toplam {len(urunler)} ürün gösterildi."
    )


def gecmisi_yazdir(islemler):

    if not islemler:

        mesaj_yaz(
            "\nİşlem geçmişi bulunamadı."
        )

        return

    print("\n" + "=" * 85)
    print(f"{'İŞLEM GEÇMİŞİ':^85}")
    print("=" * 85)

    for islem in islemler:

        print(
            f"\nİşlem ID   : {islem['id']}"
        )

        print(
            f"İşlem türü : "
            f"{islem['islem_turu']}"
        )

        print(
            f"Açıklama   : "
            f"{islem['aciklama']}"
        )

        print(
            f"Tarih      : {islem['tarih']}"
        )

        print("-" * 85)

    seslendir(
        f"Son {len(islemler)} işlem gösterildi."
    )


# --------------------------------------------------
# UYGULAMA SINIFI
# --------------------------------------------------

class StokTakipUygulamasi:

    def __init__(self):

        self.sistem = (
            StokYonetimSistemi()
        )

    @staticmethod
    def menuyu_goster():

        print("\n" + "=" * 62)
        print(
            "        47 - JSON STOK TAKİP SİSTEMİ"
        )
        print("=" * 62)
        print("1  - Yeni ürün ekle             🔒")
        print("2  - Tüm ürünleri göster")
        print("3  - Ürün ara")
        print("4  - Stok artır                 🔒")
        print("5  - Stok azalt                 🔒")
        print("6  - Ürün fiyatı güncelle       🔒")
        print("7  - Kritik stokları göster")
        print("8  - Toplam stok değerini göster")
        print("9  - Ürün sil                   🔒")
        print("10 - İşlem geçmişi              🔒")
        print("0  - Programı kapat")
        print("=" * 62)

    def baslat(self):

        mesaj_yaz(
            "\nJSON Stok Takip Sistemi başlatıldı."
        )

        while True:

            self.menuyu_goster()

            secim = input(
                "İşlem seçiniz: "
            ).strip()

            if secim == "1":
                self.urun_ekle_menu()

            elif secim == "2":
                self.tum_urunler_menu()

            elif secim == "3":
                self.urun_ara_menu()

            elif secim == "4":
                self.stok_arttir_menu()

            elif secim == "5":
                self.stok_azalt_menu()

            elif secim == "6":
                self.fiyat_guncelle_menu()

            elif secim == "7":
                self.kritik_stoklar_menu()

            elif secim == "8":
                self.toplam_deger_menu()

            elif secim == "9":
                self.urun_sil_menu()

            elif secim == "10":
                self.gecmis_menu()

            elif secim == "0":

                mesaj_yaz(
                    "\nStok takip sistemi kapatılıyor."
                )

                break

            else:

                sistemi_kapat(
                    "Geçersiz menü seçimi yapıldı."
                )

    def urun_ekle_menu(self):

        yonetici_sifresi_dogrula()

        urun_adi = input(
            "\nÜrün adı: "
        ).strip()

        kategori = input(
            "Kategori: "
        ).strip()

        try:

            adet = int(
                input(
                    "Başlangıç stok adedi: "
                )
            )

            birim_fiyat = float(
                input(
                    "Birim fiyat: "
                ).replace(",", ".")
            )

        except ValueError:

            sistemi_kapat(
                "Stok adedi veya fiyat geçersiz."
            )

            return

        if not urun_adi or not kategori:

            sistemi_kapat(
                "Ürün adı ve kategori boş bırakılamaz."
            )

        if adet < 0:

            sistemi_kapat(
                "Stok adedi negatif olamaz."
            )

        if birim_fiyat <= 0:

            sistemi_kapat(
                "Ürün fiyatı sıfırdan büyük olmalıdır."
            )

        urun_id = (
            self.sistem.urun_ekle(
                urun_adi,
                kategori,
                adet,
                birim_fiyat
            )
        )

        mesaj_yaz(
            f"\nÜrün başarıyla eklendi. "
            f"Ürün numarası {urun_id}."
        )

    def tum_urunler_menu(self):

        urunleri_yazdir(
            self.sistem.urunleri_listele(),
            "TÜM ÜRÜNLER"
        )

    def urun_ara_menu(self):

        arama_metni = input(
            "\nAranacak ürün: "
        ).strip()

        if not arama_metni:

            sistemi_kapat(
                "Arama metni boş bırakılamaz."
            )

        urunleri_yazdir(
            self.sistem.urun_ara(
                arama_metni
            ),
            "ARAMA SONUÇLARI"
        )

    def stok_arttir_menu(self):

        yonetici_sifresi_dogrula()

        try:

            urun_id = int(
                input(
                    "\nÜrün ID: "
                )
            )

            miktar = int(
                input(
                    "Eklenecek miktar: "
                )
            )

        except ValueError:

            sistemi_kapat(
                "Ürün ID veya miktar geçersiz."
            )

            return

        if miktar <= 0:

            sistemi_kapat(
                "Miktar sıfırdan büyük olmalıdır."
            )

        _, mesaj = (
            self.sistem.stok_arttir(
                urun_id,
                miktar
            )
        )

        mesaj_yaz(
            f"\n{mesaj}"
        )

    def stok_azalt_menu(self):

        yonetici_sifresi_dogrula()

        try:

            urun_id = int(
                input(
                    "\nÜrün ID: "
                )
            )

            miktar = int(
                input(
                    "Çıkarılacak miktar: "
                )
            )

        except ValueError:

            sistemi_kapat(
                "Ürün ID veya miktar geçersiz."
            )

            return

        if miktar <= 0:

            sistemi_kapat(
                "Miktar sıfırdan büyük olmalıdır."
            )

        _, mesaj = (
            self.sistem.stok_azalt(
                urun_id,
                miktar
            )
        )

        mesaj_yaz(
            f"\n{mesaj}"
        )

    def fiyat_guncelle_menu(self):

        yonetici_sifresi_dogrula()

        try:

            urun_id = int(
                input(
                    "\nÜrün ID: "
                )
            )

            yeni_fiyat = float(
                input(
                    "Yeni fiyat: "
                ).replace(",", ".")
            )

        except ValueError:

            sistemi_kapat(
                "Ürün ID veya fiyat geçersiz."
            )

            return

        if yeni_fiyat <= 0:

            sistemi_kapat(
                "Fiyat sıfırdan büyük olmalıdır."
            )

        _, mesaj = (
            self.sistem.fiyat_guncelle(
                urun_id,
                yeni_fiyat
            )
        )

        mesaj_yaz(
            f"\n{mesaj}"
        )

    def kritik_stoklar_menu(self):

        urunler = (
            self.sistem.kritik_stoklari_getir()
        )

        if urunler:

            alarm_cal()

            seslendir(
                "Kritik stok uyarısı."
            )

        urunleri_yazdir(
            urunler,
            "KRİTİK STOKLAR"
        )

    def toplam_deger_menu(self):

        toplam = (
            self.sistem.toplam_stok_degeri()
        )

        mesaj_yaz(
            f"\nToplam stok değeri: "
            f"{para_formatla(toplam)}"
        )

    def urun_sil_menu(self):

        yonetici_sifresi_dogrula()

        try:

            urun_id = int(
                input(
                    "\nSilinecek ürün ID: "
                )
            )

        except ValueError:

            sistemi_kapat(
                "Ürün ID sayı olmalıdır."
            )

            return

        onay = input(
            "Ürün tamamen silinsin mi? "
            "(EVET/HAYIR): "
        ).strip().upper()

        if onay != "EVET":

            mesaj_yaz(
                "\nSilme işlemi iptal edildi."
            )

            return

        _, mesaj = (
            self.sistem.urun_sil(
                urun_id
            )
        )

        mesaj_yaz(
            f"\n{mesaj}"
        )

    def gecmis_menu(self):

        yonetici_sifresi_dogrula()

        islemler = (
            self.sistem
            .islem_gecmisini_getir(
                limit=30
            )
        )

        gecmisi_yazdir(
            islemler
        )


# --------------------------------------------------
# PROGRAMIN BAŞLANGIÇ NOKTASI
# --------------------------------------------------

def main():

    try:

        uygulama = (
            StokTakipUygulamasi()
        )

        uygulama.baslat()

    except KeyboardInterrupt:

        print(
            "\n\nProgram kullanıcı "
            "tarafından kapatıldı."
        )

        seslendir(
            "Program kullanıcı tarafından kapatıldı."
        )

    except SystemExit:

        print(
            "\nProgram tamamen kapatıldı."
        )

    except OSError as hata:

        print(
            "\nDosya sistemi hatası oluştu:"
        )

        print(hata)

        seslendir(
            "Dosya sistemi hatası oluştu."
        )


if __name__ == "__main__":
    main()


# --------------------------------------------------
# PROGRAM SONU
# --------------------------------------------------
