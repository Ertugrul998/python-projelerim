import json
import os
import subprocess
import getpass

from datetime import datetime


# --------------------------------------------------
# SABİTLER
# --------------------------------------------------

ODA_DOSYASI = "odalar_49.json"
MUSTERI_DOSYASI = "musteriler_49.json"
REZERVASYON_DOSYASI = "rezervasyonlar_49.json"
GECMIS_DOSYASI = "otel_gecmis_49.json"

YONETICI_SIFRESI = "2580"


# --------------------------------------------------
# YARDIMCI FONKSİYONLAR
# --------------------------------------------------

def tarih_saat_al():

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


def tarih_gecerli_mi(tarih_metni):

    try:

        datetime.strptime(
            tarih_metni,
            "%Y-%m-%d"
        )

        return True

    except ValueError:
        return False


def gun_sayisi_hesapla(
    giris_tarihi,
    cikis_tarihi
):

    giris = datetime.strptime(
        giris_tarihi,
        "%Y-%m-%d"
    )

    cikis = datetime.strptime(
        cikis_tarihi,
        "%Y-%m-%d"
    )

    return (
        cikis - giris
    ).days


# --------------------------------------------------
# JSON DOSYA YÖNETİCİSİ
# --------------------------------------------------

class JSONDosyaYoneticisi:

    @staticmethod
    def dosyadan_oku(
        dosya_adi,
        varsayilan_veri
    ):

        if not os.path.exists(
            dosya_adi
        ):

            return varsayilan_veri

        try:

            with open(
                dosya_adi,
                "r",
                encoding="utf-8"
            ) as dosya:

                return json.load(
                    dosya
                )

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
# OTEL YÖNETİM SINIFI
# --------------------------------------------------

class OtelYonetimSistemi:

    def __init__(self):

        self.odalar = (
            JSONDosyaYoneticisi.dosyadan_oku(
                ODA_DOSYASI,
                []
            )
        )

        self.musteriler = (
            JSONDosyaYoneticisi.dosyadan_oku(
                MUSTERI_DOSYASI,
                []
            )
        )

        self.rezervasyonlar = (
            JSONDosyaYoneticisi.dosyadan_oku(
                REZERVASYON_DOSYASI,
                []
            )
        )

        self.gecmis = (
            JSONDosyaYoneticisi.dosyadan_oku(
                GECMIS_DOSYASI,
                []
            )
        )

        self.ornek_odalari_olustur()

    def verileri_kaydet(self):

        JSONDosyaYoneticisi.dosyaya_yaz(
            ODA_DOSYASI,
            self.odalar
        )

        JSONDosyaYoneticisi.dosyaya_yaz(
            MUSTERI_DOSYASI,
            self.musteriler
        )

        JSONDosyaYoneticisi.dosyaya_yaz(
            REZERVASYON_DOSYASI,
            self.rezervasyonlar
        )

        JSONDosyaYoneticisi.dosyaya_yaz(
            GECMIS_DOSYASI,
            self.gecmis
        )

    def ornek_odalari_olustur(self):

        if self.odalar:
            return

        self.odalar = [
            {
                "oda_no": 101,
                "oda_tipi": "TEK KİŞİLİK",
                "gunluk_fiyat": 1500.00,
                "aktif": True
            },
            {
                "oda_no": 102,
                "oda_tipi": "ÇİFT KİŞİLİK",
                "gunluk_fiyat": 2500.00,
                "aktif": True
            },
            {
                "oda_no": 201,
                "oda_tipi": "AİLE ODASI",
                "gunluk_fiyat": 3500.00,
                "aktif": True
            },
            {
                "oda_no": 301,
                "oda_tipi": "SUİT",
                "gunluk_fiyat": 5000.00,
                "aktif": True
            }
        ]

        self.verileri_kaydet()

    def yeni_musteri_id_al(self):

        if not self.musteriler:
            return 1

        return max(
            musteri["id"]
            for musteri in self.musteriler
        ) + 1

    def yeni_rezervasyon_id_al(self):

        if not self.rezervasyonlar:
            return 1

        return max(
            rezervasyon["id"]
            for rezervasyon in self.rezervasyonlar
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

        self.gecmis.append({
            "id": self.yeni_gecmis_id_al(),
            "islem_turu": islem_turu,
            "aciklama": aciklama,
            "tarih": tarih_saat_al()
        })

    def oda_bul(self, oda_no):

        for oda in self.odalar:

            if oda["oda_no"] == oda_no:
                return oda

        return None

    def musteri_bul(self, musteri_id):

        for musteri in self.musteriler:

            if musteri["id"] == musteri_id:
                return musteri

        return None

    def rezervasyon_bul(
        self,
        rezervasyon_id
    ):

        for rezervasyon in self.rezervasyonlar:

            if (
                rezervasyon["id"]
                == rezervasyon_id
            ):

                return rezervasyon

        return None

    def oda_ekle(
        self,
        oda_no,
        oda_tipi,
        gunluk_fiyat
    ):

        if self.oda_bul(oda_no):

            return (
                False,
                "Bu oda numarası zaten kayıtlı."
            )

        yeni_oda = {
            "oda_no": oda_no,
            "oda_tipi": oda_tipi,
            "gunluk_fiyat": gunluk_fiyat,
            "aktif": True
        }

        self.odalar.append(
            yeni_oda
        )

        self.gecmis_kaydet(
            "ODA EKLENDİ",
            (
                f"{oda_no} numaralı "
                f"{oda_tipi} oda eklendi."
            )
        )

        self.verileri_kaydet()

        return (
            True,
            "Oda başarıyla eklendi."
        )

    def musteri_ekle(
        self,
        ad_soyad,
        tc,
        telefon,
        eposta
    ):

        for musteri in self.musteriler:

            if musteri["tc"] == tc:

                return (
                    False,
                    "Bu TC numarası zaten kayıtlı."
                )

        yeni_musteri = {
            "id": self.yeni_musteri_id_al(),
            "ad_soyad": ad_soyad,
            "tc": tc,
            "telefon": telefon,
            "eposta": eposta,
            "kayit_tarihi": tarih_saat_al()
        }

        self.musteriler.append(
            yeni_musteri
        )

        self.gecmis_kaydet(
            "MÜŞTERİ EKLENDİ",
            (
                f"{ad_soyad} adlı müşteri "
                "sisteme kaydedildi."
            )
        )

        self.verileri_kaydet()

        return (
            True,
            yeni_musteri["id"]
        )

    def oda_tarih_cakismasi_var_mi(
        self,
        oda_no,
        giris_tarihi,
        cikis_tarihi
    ):

        yeni_giris = datetime.strptime(
            giris_tarihi,
            "%Y-%m-%d"
        )

        yeni_cikis = datetime.strptime(
            cikis_tarihi,
            "%Y-%m-%d"
        )

        for rezervasyon in self.rezervasyonlar:

            if (
                rezervasyon["oda_no"] != oda_no
                or rezervasyon["durum"]
                in ["İPTAL", "CHECK-OUT"]
            ):

                continue

            mevcut_giris = datetime.strptime(
                rezervasyon["giris_tarihi"],
                "%Y-%m-%d"
            )

            mevcut_cikis = datetime.strptime(
                rezervasyon["cikis_tarihi"],
                "%Y-%m-%d"
            )

            if (
                yeni_giris < mevcut_cikis
                and yeni_cikis > mevcut_giris
            ):

                return True

        return False

    def rezervasyon_olustur(
        self,
        musteri_id,
        oda_no,
        giris_tarihi,
        cikis_tarihi
    ):

        musteri = self.musteri_bul(
            musteri_id
        )

        oda = self.oda_bul(
            oda_no
        )

        if musteri is None:

            return (
                False,
                "Müşteri bulunamadı."
            )

        if oda is None:

            return (
                False,
                "Oda bulunamadı."
            )

        if not oda["aktif"]:

            return (
                False,
                "Bu oda kullanıma kapalı."
            )

        if self.oda_tarih_cakismasi_var_mi(
            oda_no,
            giris_tarihi,
            cikis_tarihi
        ):

            alarm_cal()

            seslendir(
                "Rezervasyon çakışması algılandı."
            )

            return (
                False,
                (
                    "Bu oda seçilen tarihler "
                    "arasında müsait değil."
                )
            )

        gun_sayisi = gun_sayisi_hesapla(
            giris_tarihi,
            cikis_tarihi
        )

        if gun_sayisi <= 0:

            sistemi_kapat(
                (
                    "Çıkış tarihi giriş "
                    "tarihinden sonra olmalıdır."
                )
            )

        toplam_ucret = (
            gun_sayisi
            * oda["gunluk_fiyat"]
        )

        yeni_rezervasyon = {
            "id": self.yeni_rezervasyon_id_al(),
            "musteri_id": musteri_id,
            "musteri_adi": musteri["ad_soyad"],
            "oda_no": oda_no,
            "oda_tipi": oda["oda_tipi"],
            "giris_tarihi": giris_tarihi,
            "cikis_tarihi": cikis_tarihi,
            "gun_sayisi": gun_sayisi,
            "gunluk_fiyat": oda["gunluk_fiyat"],
            "toplam_ucret": toplam_ucret,
            "durum": "REZERVE",
            "olusturma_tarihi": tarih_saat_al(),
            "check_in_tarihi": None,
            "check_out_tarihi": None
        }

        self.rezervasyonlar.append(
            yeni_rezervasyon
        )

        self.gecmis_kaydet(
            "REZERVASYON OLUŞTURULDU",
            (
                f"{musteri['ad_soyad']} için "
                f"{oda_no} numaralı oda "
                "rezerve edildi."
            )
        )

        self.verileri_kaydet()

        return (
            True,
            yeni_rezervasyon
        )

    def check_in_yap(
        self,
        rezervasyon_id
    ):

        rezervasyon = self.rezervasyon_bul(
            rezervasyon_id
        )

        if rezervasyon is None:

            return (
                False,
                "Rezervasyon bulunamadı."
            )

        if rezervasyon["durum"] == "CHECK-IN":

            return (
                False,
                "Check-in daha önce yapılmış."
            )

        if rezervasyon["durum"] == "CHECK-OUT":

            return (
                False,
                "Tamamlanmış rezervasyona check-in yapılamaz."
            )

        if rezervasyon["durum"] == "İPTAL":

            return (
                False,
                "İptal edilmiş rezervasyona check-in yapılamaz."
            )

        rezervasyon["durum"] = "CHECK-IN"
        rezervasyon["check_in_tarihi"] = tarih_saat_al()

        self.gecmis_kaydet(
            "CHECK-IN",
            (
                f"{rezervasyon['musteri_adi']} "
                f"{rezervasyon['oda_no']} "
                "numaralı odaya giriş yaptı."
            )
        )

        self.verileri_kaydet()

        return (
            True,
            "Check-in başarıyla tamamlandı."
        )

    def check_out_yap(
        self,
        rezervasyon_id
    ):

        rezervasyon = self.rezervasyon_bul(
            rezervasyon_id
        )

        if rezervasyon is None:

            return (
                False,
                "Rezervasyon bulunamadı."
            )

        if rezervasyon["durum"] != "CHECK-IN":

            return (
                False,
                "Check-in yapılmadan check-out yapılamaz."
            )

        rezervasyon["durum"] = "CHECK-OUT"
        rezervasyon["check_out_tarihi"] = tarih_saat_al()

        self.gecmis_kaydet(
            "CHECK-OUT",
            (
                f"{rezervasyon['musteri_adi']} "
                f"{rezervasyon['oda_no']} "
                "numaralı odadan çıkış yaptı."
            )
        )

        self.verileri_kaydet()

        return (
            True,
            "Check-out başarıyla tamamlandı."
        )

    def rezervasyon_iptal_et(
        self,
        rezervasyon_id
    ):

        rezervasyon = self.rezervasyon_bul(
            rezervasyon_id
        )

        if rezervasyon is None:

            return (
                False,
                "Rezervasyon bulunamadı."
            )

        if rezervasyon["durum"] == "CHECK-IN":

            sistemi_kapat(
                (
                    "Check-in yapılmış rezervasyon "
                    "iptal edilemez."
                ),
                alarm=True
            )

        if rezervasyon["durum"] == "CHECK-OUT":

            return (
                False,
                "Tamamlanmış rezervasyon iptal edilemez."
            )

        if rezervasyon["durum"] == "İPTAL":

            return (
                False,
                "Rezervasyon zaten iptal edilmiş."
            )

        rezervasyon["durum"] = "İPTAL"

        self.gecmis_kaydet(
            "REZERVASYON İPTAL",
            (
                f"{rezervasyon['musteri_adi']} "
                f"adlı müşterinin {rezervasyon['oda_no']} "
                "numaralı oda rezervasyonu iptal edildi."
            )
        )

        self.verileri_kaydet()

        return (
            True,
            "Rezervasyon başarıyla iptal edildi."
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

def odalari_yazdir(odalar):

    if not odalar:

        mesaj_yaz(
            "\nOda kaydı bulunamadı."
        )

        return

    print("\n" + "=" * 75)
    print(f"{'ODA LİSTESİ':^75}")
    print("=" * 75)

    for oda in odalar:

        durum = (
            "AKTİF"
            if oda["aktif"]
            else "KAPALI"
        )

        print(
            f"\nOda numarası : {oda['oda_no']}"
        )

        print(
            f"Oda tipi     : {oda['oda_tipi']}"
        )

        print(
            f"Günlük fiyat : "
            f"{para_formatla(oda['gunluk_fiyat'])}"
        )

        print(
            f"Durum        : {durum}"
        )

        print("-" * 75)

    seslendir(
        f"Toplam {len(odalar)} oda gösterildi."
    )


def musterileri_yazdir(musteriler):

    if not musteriler:

        mesaj_yaz(
            "\nMüşteri kaydı bulunamadı."
        )

        return

    print("\n" + "=" * 75)
    print(f"{'MÜŞTERİ LİSTESİ':^75}")
    print("=" * 75)

    for musteri in musteriler:

        print(
            f"\nMüşteri ID   : {musteri['id']}"
        )

        print(
            f"Ad soyad      : {musteri['ad_soyad']}"
        )

        print(
            f"TC            : {musteri['tc']}"
        )

        print(
            f"Telefon       : {musteri['telefon']}"
        )

        print(
            f"E-posta       : {musteri['eposta']}"
        )

        print(
            f"Kayıt tarihi  : {musteri['kayit_tarihi']}"
        )

        print("-" * 75)

    seslendir(
        f"Toplam {len(musteriler)} müşteri gösterildi."
    )


def rezervasyonlari_yazdir(
    rezervasyonlar,
    baslik
):

    if not rezervasyonlar:

        mesaj_yaz(
            "\nRezervasyon kaydı bulunamadı."
        )

        return

    print("\n" + "=" * 85)
    print(f"{baslik:^85}")
    print("=" * 85)

    for rezervasyon in rezervasyonlar:

        print(
            f"\nRezervasyon ID : {rezervasyon['id']}"
        )

        print(
            f"Müşteri        : {rezervasyon['musteri_adi']}"
        )

        print(
            f"Oda numarası   : {rezervasyon['oda_no']}"
        )

        print(
            f"Oda tipi       : {rezervasyon['oda_tipi']}"
        )

        print(
            f"Giriş tarihi   : {rezervasyon['giris_tarihi']}"
        )

        print(
            f"Çıkış tarihi   : {rezervasyon['cikis_tarihi']}"
        )

        print(
            f"Gün sayısı     : {rezervasyon['gun_sayisi']}"
        )

        print(
            f"Toplam ücret   : "
            f"{para_formatla(rezervasyon['toplam_ucret'])}"
        )

        print(
            f"Durum          : {rezervasyon['durum']}"
        )

        print(
            f"Check-in       : "
            f"{rezervasyon['check_in_tarihi'] or '-'}"
        )

        print(
            f"Check-out      : "
            f"{rezervasyon['check_out_tarihi'] or '-'}"
        )

        print("-" * 85)

    seslendir(
        f"Toplam {len(rezervasyonlar)} rezervasyon gösterildi."
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
            f"İşlem türü : {islem['islem_turu']}"
        )

        print(
            f"Açıklama   : {islem['aciklama']}"
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

class OtelRezervasyonUygulamasi:

    def __init__(self):

        self.sistem = (
            OtelYonetimSistemi()
        )

    @staticmethod
    def menuyu_goster():

        print("\n" + "=" * 66)
        print(
            "       49 - JSON OTEL REZERVASYON SİSTEMİ"
        )
        print("=" * 66)
        print("1  - Yeni oda ekle              🔒")
        print("2  - Odaları listele")
        print("3  - Yeni müşteri ekle          🔒")
        print("4  - Müşterileri listele")
        print("5  - Rezervasyon oluştur        🔒")
        print("6  - Rezervasyonları listele")
        print("7  - Check-in yap               🔒")
        print("8  - Check-out yap              🔒")
        print("9  - Rezervasyon iptal et       🔒")
        print("10 - İşlem geçmişi              🔒")
        print("0  - Programı kapat")
        print("=" * 66)

    def baslat(self):

        mesaj_yaz(
            "\nJSON Otel Rezervasyon "
            "Sistemi başlatıldı."
        )

        while True:

            self.menuyu_goster()

            secim = input(
                "İşlem seçiniz: "
            ).strip()

            if secim == "1":
                self.oda_ekle_menu()

            elif secim == "2":
                self.odalar_menu()

            elif secim == "3":
                self.musteri_ekle_menu()

            elif secim == "4":
                self.musteriler_menu()

            elif secim == "5":
                self.rezervasyon_olustur_menu()

            elif secim == "6":
                self.rezervasyonlar_menu()

            elif secim == "7":
                self.check_in_menu()

            elif secim == "8":
                self.check_out_menu()

            elif secim == "9":
                self.rezervasyon_iptal_menu()

            elif secim == "10":
                self.gecmis_menu()

            elif secim == "0":

                mesaj_yaz(
                    "\nOtel rezervasyon "
                    "sistemi kapatılıyor."
                )

                break

            else:

                sistemi_kapat(
                    "Geçersiz menü seçimi yapıldı."
                )

    def oda_ekle_menu(self):

        yonetici_sifresi_dogrula()

        try:

            oda_no = int(
                input(
                    "\nOda numarası: "
                )
            )

            gunluk_fiyat = float(
                input(
                    "Günlük fiyat: "
                ).replace(",", ".")
            )

        except ValueError:

            sistemi_kapat(
                "Oda numarası veya fiyat geçersiz."
            )

            return

        oda_tipi = input(
            "Oda tipi: "
        ).strip().upper()

        if not oda_tipi:

            sistemi_kapat(
                "Oda tipi boş bırakılamaz."
            )

        if gunluk_fiyat <= 0:

            sistemi_kapat(
                "Oda fiyatı sıfırdan büyük olmalıdır."
            )

        _, mesaj = (
            self.sistem.oda_ekle(
                oda_no,
                oda_tipi,
                gunluk_fiyat
            )
        )

        mesaj_yaz(
            f"\n{mesaj}"
        )

    def odalar_menu(self):

        odalari_yazdir(
            self.sistem.odalar
        )

    def musteri_ekle_menu(self):

        yonetici_sifresi_dogrula()

        ad_soyad = input(
            "\nMüşteri ad soyad: "
        ).strip()

        tc = input(
            "TC kimlik numarası: "
        ).strip()

        telefon = input(
            "Telefon: "
        ).strip()

        eposta = input(
            "E-posta: "
        ).strip().lower()

        if not all([
            ad_soyad,
            tc,
            telefon,
            eposta
        ]):

            sistemi_kapat(
                "Müşteri bilgileri boş bırakılamaz."
            )

        if not tc.isdigit() or len(tc) != 11:

            sistemi_kapat(
                "TC kimlik numarası 11 rakam olmalıdır."
            )

        basarili, sonuc = (
            self.sistem.musteri_ekle(
                ad_soyad,
                tc,
                telefon,
                eposta
            )
        )

        if basarili:

            mesaj_yaz(
                f"\nMüşteri başarıyla eklendi. "
                f"Müşteri numarası {sonuc}."
            )

        else:

            mesaj_yaz(
                f"\n{sonuc}"
            )

    def musteriler_menu(self):

        musterileri_yazdir(
            self.sistem.musteriler
        )

    def rezervasyon_olustur_menu(self):

        yonetici_sifresi_dogrula()

        try:

            musteri_id = int(
                input(
                    "\nMüşteri ID: "
                )
            )

            oda_no = int(
                input(
                    "Oda numarası: "
                )
            )

        except ValueError:

            sistemi_kapat(
                "Müşteri ID veya oda numarası geçersiz."
            )

            return

        giris_tarihi = input(
            "Giriş tarihi (YYYY-AA-GG): "
        ).strip()

        cikis_tarihi = input(
            "Çıkış tarihi (YYYY-AA-GG): "
        ).strip()

        if not tarih_gecerli_mi(
            giris_tarihi
        ):

            sistemi_kapat(
                "Giriş tarihi geçersiz."
            )

        if not tarih_gecerli_mi(
            cikis_tarihi
        ):

            sistemi_kapat(
                "Çıkış tarihi geçersiz."
            )

        basarili, sonuc = (
            self.sistem.rezervasyon_olustur(
                musteri_id,
                oda_no,
                giris_tarihi,
                cikis_tarihi
            )
        )

        if not basarili:

            mesaj_yaz(
                f"\n{sonuc}"
            )

            return

        mesaj_yaz(
            "\nRezervasyon başarıyla oluşturuldu."
        )

        print(
            f"Rezervasyon numarası: {sonuc['id']}"
        )

        print(
            f"Toplam ücret: "
            f"{para_formatla(sonuc['toplam_ucret'])}"
        )

    def rezervasyonlar_menu(self):

        rezervasyonlari_yazdir(
            self.sistem.rezervasyonlar,
            "TÜM REZERVASYONLAR"
        )

    def check_in_menu(self):

        yonetici_sifresi_dogrula()

        try:

            rezervasyon_id = int(
                input(
                    "\nRezervasyon ID: "
                )
            )

        except ValueError:

            sistemi_kapat(
                "Rezervasyon ID sayı olmalıdır."
            )

            return

        _, mesaj = (
            self.sistem.check_in_yap(
                rezervasyon_id
            )
        )

        mesaj_yaz(
            f"\n{mesaj}"
        )

    def check_out_menu(self):

        yonetici_sifresi_dogrula()

        try:

            rezervasyon_id = int(
                input(
                    "\nRezervasyon ID: "
                )
            )

        except ValueError:

            sistemi_kapat(
                "Rezervasyon ID sayı olmalıdır."
            )

            return

        _, mesaj = (
            self.sistem.check_out_yap(
                rezervasyon_id
            )
        )

        mesaj_yaz(
            f"\n{mesaj}"
        )

    def rezervasyon_iptal_menu(self):

        yonetici_sifresi_dogrula()

        try:

            rezervasyon_id = int(
                input(
                    "\nİptal edilecek rezervasyon ID: "
                )
            )

        except ValueError:

            sistemi_kapat(
                "Rezervasyon ID sayı olmalıdır."
            )

            return

        _, mesaj = (
            self.sistem.rezervasyon_iptal_et(
                rezervasyon_id
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
            OtelRezervasyonUygulamasi()
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