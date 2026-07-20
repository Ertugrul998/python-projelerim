import json
import os
import subprocess
import getpass
import sys

from datetime import datetime


# --------------------------------------------------
# SABİTLER
# --------------------------------------------------

PERSONEL_DOSYASI = "personeller_46.json"
GECMIS_DOSYASI = "personel_gecmis_46.json"

YONETICI_SIFRESI = "2580"


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


def sistemi_kapat(mesaj):

    print("\n" + "!" * 55)
    print(mesaj)
    print("Sistem güvenlik nedeniyle kapatılıyor.")
    print("!" * 55)

    seslendir(mesaj)
    seslendir(
        "Sistem güvenlik nedeniyle kapatılıyor."
    )

    sys.exit()


def yonetici_sifresi_dogrula():

    sifre = guvenli_sifre_al(
        "\nYönetici şifresini giriniz: "
    )

    if sifre == YONETICI_SIFRESI:

        mesaj_yaz(
            "\nŞifre doğru. Yetki verildi."
        )

        return True

    sistemi_kapat(
        "Yanlış yönetici şifresi girildi."
    )

    return False


def para_formatla(miktar):

    return (
        f"{miktar:,.2f} TL"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


# --------------------------------------------------
# JSON DOSYA İŞLEMLERİ
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
                f"{dosya_adi} dosyası bozulmuş."
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

            if os.path.exists(
                gecici_dosya
            ):

                try:
                    os.remove(
                        gecici_dosya
                    )

                except OSError:
                    pass

            sistemi_kapat(
                f"Dosya kaydedilemedi. {hata}"
            )


# --------------------------------------------------
# PERSONEL YÖNETİM SINIFI
# --------------------------------------------------

class PersonelYonetimSistemi:

    def __init__(self):

        self.personeller = (
            JSONDosyaYoneticisi.dosyadan_oku(
                PERSONEL_DOSYASI,
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
            PERSONEL_DOSYASI,
            self.personeller
        )

        JSONDosyaYoneticisi.dosyaya_yaz(
            GECMIS_DOSYASI,
            self.gecmis
        )

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

    def yeni_gecmis_id_al(self):

        if not self.gecmis:
            return 1

        return max(
            kayit["id"]
            for kayit in self.gecmis
        ) + 1

    def yeni_personel_id_al(self):

        if not self.personeller:
            return 1

        return max(
            personel["id"]
            for personel in self.personeller
        ) + 1

    def personel_bul(self, personel_id):

        for personel in self.personeller:

            if personel["id"] == personel_id:
                return personel

        return None

    def personel_ekle(
        self,
        ad_soyad,
        departman,
        pozisyon,
        maas,
        telefon,
        eposta
    ):

        yeni_personel = {
            "id": self.yeni_personel_id_al(),
            "ad_soyad": ad_soyad,
            "departman": departman,
            "pozisyon": pozisyon,
            "maas": maas,
            "telefon": telefon,
            "eposta": eposta,
            "aktif": True,
            "kayit_tarihi": tarih_al(),
            "guncelleme_tarihi": None
        }

        self.personeller.append(
            yeni_personel
        )

        self.gecmis_kaydet(
            "PERSONEL EKLENDİ",
            (
                f"{ad_soyad} adlı personel "
                f"{departman} departmanına eklendi."
            )
        )

        self.verileri_kaydet()

        return yeni_personel["id"]

    def personelleri_listele(
        self,
        sadece_aktif=True
    ):

        if sadece_aktif:

            return [
                personel
                for personel in self.personeller
                if personel["aktif"]
            ]

        return self.personeller

    def personel_ara(self, arama_metni):

        arama_metni = (
            arama_metni.lower()
        )

        sonuclar = []

        for personel in self.personeller:

            bilgiler = (
                f"{personel['ad_soyad']} "
                f"{personel['departman']} "
                f"{personel['pozisyon']} "
                f"{personel['telefon']} "
                f"{personel['eposta']}"
            ).lower()

            if arama_metni in bilgiler:

                sonuclar.append(
                    personel
                )

        return sonuclar

    def maas_guncelle(
        self,
        personel_id,
        yeni_maas
    ):

        personel = self.personel_bul(
            personel_id
        )

        if personel is None:

            return (
                False,
                "Personel bulunamadı."
            )

        if not personel["aktif"]:

            return (
                False,
                "Pasif personelin maaşı güncellenemez."
            )

        eski_maas = personel["maas"]

        personel["maas"] = yeni_maas
        personel["guncelleme_tarihi"] = tarih_al()

        self.gecmis_kaydet(
            "MAAŞ GÜNCELLENDİ",
            (
                f"{personel['ad_soyad']} adlı "
                f"personelin maaşı "
                f"{para_formatla(eski_maas)} "
                f"tutarından "
                f"{para_formatla(yeni_maas)} "
                "tutarına güncellendi."
            )
        )

        self.verileri_kaydet()

        return (
            True,
            "Maaş başarıyla güncellendi."
        )

    def personel_bilgisi_guncelle(
        self,
        personel_id,
        departman,
        pozisyon,
        telefon,
        eposta
    ):

        personel = self.personel_bul(
            personel_id
        )

        if personel is None:

            return (
                False,
                "Personel bulunamadı."
            )

        if not personel["aktif"]:

            return (
                False,
                "Pasif personel güncellenemez."
            )

        personel["departman"] = departman
        personel["pozisyon"] = pozisyon
        personel["telefon"] = telefon
        personel["eposta"] = eposta
        personel["guncelleme_tarihi"] = tarih_al()

        self.gecmis_kaydet(
            "PERSONEL GÜNCELLENDİ",
            (
                f"{personel['ad_soyad']} adlı "
                "personelin bilgileri güncellendi."
            )
        )

        self.verileri_kaydet()

        return (
            True,
            "Personel bilgileri güncellendi."
        )

    def personel_pasif_yap(
        self,
        personel_id
    ):

        personel = self.personel_bul(
            personel_id
        )

        if personel is None:

            return (
                False,
                "Personel bulunamadı."
            )

        if not personel["aktif"]:

            return (
                False,
                "Personel zaten pasif durumda."
            )

        personel["aktif"] = False
        personel["guncelleme_tarihi"] = tarih_al()

        self.gecmis_kaydet(
            "PERSONEL PASİF YAPILDI",
            (
                f"{personel['ad_soyad']} adlı "
                "personel pasif duruma getirildi."
            )
        )

        self.verileri_kaydet()

        return (
            True,
            "Personel pasif duruma getirildi."
        )

    def personel_aktif_yap(
        self,
        personel_id
    ):

        personel = self.personel_bul(
            personel_id
        )

        if personel is None:

            return (
                False,
                "Personel bulunamadı."
            )

        if personel["aktif"]:

            return (
                False,
                "Personel zaten aktif durumda."
            )

        personel["aktif"] = True
        personel["guncelleme_tarihi"] = tarih_al()

        self.gecmis_kaydet(
            "PERSONEL AKTİF YAPILDI",
            (
                f"{personel['ad_soyad']} adlı "
                "personel yeniden aktif yapıldı."
            )
        )

        self.verileri_kaydet()

        return (
            True,
            "Personel yeniden aktif yapıldı."
        )

    def personel_tamamen_sil(
        self,
        personel_id
    ):

        personel = self.personel_bul(
            personel_id
        )

        if personel is None:

            return (
                False,
                "Personel bulunamadı."
            )

        personel_adi = personel[
            "ad_soyad"
        ]

        self.personeller.remove(
            personel
        )

        self.gecmis_kaydet(
            "PERSONEL SİLİNDİ",
            (
                f"{personel_adi} adlı personel "
                "sistemden tamamen silindi."
            )
        )

        self.verileri_kaydet()

        return (
            True,
            "Personel sistemden tamamen silindi."
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

def personelleri_yazdir(
    personeller,
    baslik
):

    if not personeller:

        mesaj_yaz(
            "\nPersonel kaydı bulunamadı."
        )

        return

    print("\n" + "=" * 80)
    print(f"{baslik:^80}")
    print("=" * 80)

    for personel in personeller:

        durum = (
            "AKTİF"
            if personel["aktif"]
            else "PASİF"
        )

        print(
            f"\nPersonel ID      : "
            f"{personel['id']}"
        )

        print(
            f"Ad soyad         : "
            f"{personel['ad_soyad']}"
        )

        print(
            f"Departman        : "
            f"{personel['departman']}"
        )

        print(
            f"Pozisyon         : "
            f"{personel['pozisyon']}"
        )

        print(
            f"Maaş             : "
            f"{para_formatla(personel['maas'])}"
        )

        print(
            f"Telefon          : "
            f"{personel['telefon']}"
        )

        print(
            f"E-posta          : "
            f"{personel['eposta']}"
        )

        print(
            f"Durum            : {durum}"
        )

        print(
            f"Kayıt tarihi     : "
            f"{personel['kayit_tarihi']}"
        )

        print(
            f"Güncelleme tarihi: "
            f"{personel['guncelleme_tarihi'] or '-'}"
        )

        print("-" * 80)

    seslendir(
        f"Toplam {len(personeller)} "
        "personel gösterildi."
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
        f"Son {len(islemler)} "
        "işlem gösterildi."
    )


# --------------------------------------------------
# UYGULAMA SINIFI
# --------------------------------------------------

class PersonelTakipUygulamasi:

    def __init__(self):

        self.sistem = (
            PersonelYonetimSistemi()
        )

    @staticmethod
    def menuyu_goster():

        print("\n" + "=" * 62)
        print(
            "       46 - JSON PERSONEL TAKİP SİSTEMİ"
        )
        print("=" * 62)
        print("1 - Yeni personel ekle          🔒")
        print("2 - Aktif personelleri göster")
        print("3 - Tüm personelleri göster")
        print("4 - Personel ara")
        print("5 - Maaş güncelle               🔒")
        print("6 - Personel bilgisi güncelle   🔒")
        print("7 - Personeli pasif yap         🔒")
        print("8 - Personeli aktif yap         🔒")
        print("9 - Personeli tamamen sil       🔒")
        print("10 - İşlem geçmişi              🔒")
        print("0 - Programı kapat")
        print("=" * 62)

    def baslat(self):

        mesaj_yaz(
            "\nJSON Personel Takip "
            "Sistemi başlatıldı."
        )

        while True:

            self.menuyu_goster()

            secim = input(
                "İşlem seçiniz: "
            ).strip()

            if secim == "1":
                self.personel_ekle_menu()

            elif secim == "2":
                self.aktif_personeller_menu()

            elif secim == "3":
                self.tum_personeller_menu()

            elif secim == "4":
                self.personel_ara_menu()

            elif secim == "5":
                self.maas_guncelle_menu()

            elif secim == "6":
                self.personel_guncelle_menu()

            elif secim == "7":
                self.personel_pasif_menu()

            elif secim == "8":
                self.personel_aktif_menu()

            elif secim == "9":
                self.personel_sil_menu()

            elif secim == "10":
                self.gecmis_menu()

            elif secim == "0":

                mesaj_yaz(
                    "\nPersonel takip "
                    "sistemi kapatılıyor."
                )

                break

            else:

                sistemi_kapat(
                    "Geçersiz menü seçimi yapıldı."
                )

    def personel_ekle_menu(self):

        yonetici_sifresi_dogrula()

        ad_soyad = input(
            "\nAd soyad: "
        ).strip()

        departman = input(
            "Departman: "
        ).strip()

        pozisyon = input(
            "Pozisyon: "
        ).strip()

        maas_metni = input(
            "Maaş: "
        ).replace(",", ".").strip()

        telefon = input(
            "Telefon: "
        ).strip()

        eposta = input(
            "E-posta: "
        ).strip().lower()

        if not all([
            ad_soyad,
            departman,
            pozisyon,
            maas_metni,
            telefon,
            eposta
        ]):

            sistemi_kapat(
                "Personel bilgileri boş bırakılamaz."
            )

        try:

            maas = float(
                maas_metni
            )

        except ValueError:

            sistemi_kapat(
                "Maaş alanına geçersiz değer girildi."
            )

            return

        if maas <= 0:

            sistemi_kapat(
                "Maaş sıfırdan büyük olmalıdır."
            )

        personel_id = (
            self.sistem.personel_ekle(
                ad_soyad,
                departman,
                pozisyon,
                maas,
                telefon,
                eposta
            )
        )

        mesaj_yaz(
            f"\nPersonel başarıyla eklendi. "
            f"Personel numarası {personel_id}."
        )

    def aktif_personeller_menu(self):

        personeller = (
            self.sistem
            .personelleri_listele(
                sadece_aktif=True
            )
        )

        personelleri_yazdir(
            personeller,
            "AKTİF PERSONELLER"
        )

    def tum_personeller_menu(self):

        personeller = (
            self.sistem
            .personelleri_listele(
                sadece_aktif=False
            )
        )

        personelleri_yazdir(
            personeller,
            "TÜM PERSONELLER"
        )

    def personel_ara_menu(self):

        arama_metni = input(
            "\nAranacak personel: "
        ).strip()

        if not arama_metni:

            sistemi_kapat(
                "Arama metni boş bırakılamaz."
            )

        sonuclar = (
            self.sistem.personel_ara(
                arama_metni
            )
        )

        personelleri_yazdir(
            sonuclar,
            "ARAMA SONUÇLARI"
        )

    def maas_guncelle_menu(self):

        yonetici_sifresi_dogrula()

        try:

            personel_id = int(
                input(
                    "\nPersonel ID: "
                )
            )

            yeni_maas = float(
                input(
                    "Yeni maaş: "
                ).replace(",", ".")
            )

        except ValueError:

            sistemi_kapat(
                "Personel ID veya maaş geçersiz."
            )

            return

        if yeni_maas <= 0:

            sistemi_kapat(
                "Maaş sıfırdan büyük olmalıdır."
            )

        _, mesaj = (
            self.sistem.maas_guncelle(
                personel_id,
                yeni_maas
            )
        )

        mesaj_yaz(
            f"\n{mesaj}"
        )

    def personel_guncelle_menu(self):

        yonetici_sifresi_dogrula()

        try:

            personel_id = int(
                input(
                    "\nPersonel ID: "
                )
            )

        except ValueError:

            sistemi_kapat(
                "Personel ID sayı olmalıdır."
            )

            return

        departman = input(
            "Yeni departman: "
        ).strip()

        pozisyon = input(
            "Yeni pozisyon: "
        ).strip()

        telefon = input(
            "Yeni telefon: "
        ).strip()

        eposta = input(
            "Yeni e-posta: "
        ).strip().lower()

        if not all([
            departman,
            pozisyon,
            telefon,
            eposta
        ]):

            sistemi_kapat(
                "Personel bilgileri boş bırakılamaz."
            )

        _, mesaj = (
            self.sistem
            .personel_bilgisi_guncelle(
                personel_id,
                departman,
                pozisyon,
                telefon,
                eposta
            )
        )

        mesaj_yaz(
            f"\n{mesaj}"
        )

    def personel_pasif_menu(self):

        yonetici_sifresi_dogrula()

        try:

            personel_id = int(
                input(
                    "\nPasif yapılacak personel ID: "
                )
            )

        except ValueError:

            sistemi_kapat(
                "Personel ID sayı olmalıdır."
            )

            return

        _, mesaj = (
            self.sistem.personel_pasif_yap(
                personel_id
            )
        )

        mesaj_yaz(
            f"\n{mesaj}"
        )

    def personel_aktif_menu(self):

        yonetici_sifresi_dogrula()

        try:

            personel_id = int(
                input(
                    "\nAktif yapılacak personel ID: "
                )
            )

        except ValueError:

            sistemi_kapat(
                "Personel ID sayı olmalıdır."
            )

            return

        _, mesaj = (
            self.sistem.personel_aktif_yap(
                personel_id
            )
        )

        mesaj_yaz(
            f"\n{mesaj}"
        )

    def personel_sil_menu(self):

        yonetici_sifresi_dogrula()

        try:

            personel_id = int(
                input(
                    "\nSilinecek personel ID: "
                )
            )

        except ValueError:

            sistemi_kapat(
                "Personel ID sayı olmalıdır."
            )

            return

        onay = input(
            "Personel tamamen silinsin mi? "
            "(EVET/HAYIR): "
        ).strip().upper()

        if onay != "EVET":

            mesaj_yaz(
                "\nSilme işlemi iptal edildi."
            )

            return

        _, mesaj = (
            self.sistem.personel_tamamen_sil(
                personel_id
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
            PersonelTakipUygulamasi()
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