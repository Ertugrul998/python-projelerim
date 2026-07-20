import json
import os
import subprocess
import getpass

from datetime import datetime


# --------------------------------------------------
# SABİTLER
# --------------------------------------------------

HASTA_DOSYASI = "hastalar_48.json"
DOKTOR_DOSYASI = "doktorlar_48.json"
RANDEVU_DOSYASI = "randevular_48.json"
GECMIS_DOSYASI = "hastane_gecmis_48.json"

YONETICI_SIFRESI = "2580"


# --------------------------------------------------
# YARDIMCI FONKSİYONLAR
# --------------------------------------------------

def tarih_saat_al():

    return datetime.now().strftime(
        "%d.%m.%Y %H:%M:%S"
    )


def bugunun_tarihi():

    return datetime.now().strftime(
        "%Y-%m-%d"
    )


def tarih_goster(tarih_metni):

    try:

        tarih = datetime.strptime(
            tarih_metni,
            "%Y-%m-%d"
        )

        return tarih.strftime(
            "%d.%m.%Y"
        )

    except ValueError:
        return tarih_metni


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


def tarih_saat_gecerli_mi(
    tarih_metni,
    saat_metni
):

    try:

        datetime.strptime(
            f"{tarih_metni} {saat_metni}",
            "%Y-%m-%d %H:%M"
        )

        return True

    except ValueError:
        return False


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
# HASTANE YÖNETİM SINIFI
# --------------------------------------------------

class HastaneYonetimSistemi:

    def __init__(self):

        self.hastalar = (
            JSONDosyaYoneticisi.dosyadan_oku(
                HASTA_DOSYASI,
                []
            )
        )

        self.doktorlar = (
            JSONDosyaYoneticisi.dosyadan_oku(
                DOKTOR_DOSYASI,
                []
            )
        )

        self.randevular = (
            JSONDosyaYoneticisi.dosyadan_oku(
                RANDEVU_DOSYASI,
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
            HASTA_DOSYASI,
            self.hastalar
        )

        JSONDosyaYoneticisi.dosyaya_yaz(
            DOKTOR_DOSYASI,
            self.doktorlar
        )

        JSONDosyaYoneticisi.dosyaya_yaz(
            RANDEVU_DOSYASI,
            self.randevular
        )

        JSONDosyaYoneticisi.dosyaya_yaz(
            GECMIS_DOSYASI,
            self.gecmis
        )

    def yeni_hasta_id_al(self):

        if not self.hastalar:
            return 1

        return max(
            hasta["id"]
            for hasta in self.hastalar
        ) + 1

    def yeni_doktor_id_al(self):

        if not self.doktorlar:
            return 1

        return max(
            doktor["id"]
            for doktor in self.doktorlar
        ) + 1

    def yeni_randevu_id_al(self):

        if not self.randevular:
            return 1

        return max(
            randevu["id"]
            for randevu in self.randevular
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

    def hasta_bul(self, hasta_id):

        for hasta in self.hastalar:

            if hasta["id"] == hasta_id:
                return hasta

        return None

    def doktor_bul(self, doktor_id):

        for doktor in self.doktorlar:

            if doktor["id"] == doktor_id:
                return doktor

        return None

    def randevu_bul(self, randevu_id):

        for randevu in self.randevular:

            if randevu["id"] == randevu_id:
                return randevu

        return None

    def hasta_ekle(
        self,
        ad_soyad,
        tc,
        telefon,
        eposta
    ):

        for hasta in self.hastalar:

            if hasta["tc"] == tc:

                return (
                    False,
                    "Bu TC kimlik numarası zaten kayıtlı."
                )

        yeni_hasta = {
            "id": self.yeni_hasta_id_al(),
            "ad_soyad": ad_soyad,
            "tc": tc,
            "telefon": telefon,
            "eposta": eposta,
            "aktif": True,
            "kayit_tarihi": tarih_saat_al()
        }

        self.hastalar.append(
            yeni_hasta
        )

        self.gecmis_kaydet(
            "HASTA EKLENDİ",
            (
                f"{ad_soyad} adlı hasta "
                "sisteme kaydedildi."
            )
        )

        self.verileri_kaydet()

        return (
            True,
            yeni_hasta["id"]
        )

    def doktor_ekle(
        self,
        ad_soyad,
        bolum,
        telefon,
        eposta
    ):

        yeni_doktor = {
            "id": self.yeni_doktor_id_al(),
            "ad_soyad": ad_soyad,
            "bolum": bolum,
            "telefon": telefon,
            "eposta": eposta,
            "aktif": True,
            "kayit_tarihi": tarih_saat_al()
        }

        self.doktorlar.append(
            yeni_doktor
        )

        self.gecmis_kaydet(
            "DOKTOR EKLENDİ",
            (
                f"{ad_soyad} adlı doktor "
                f"{bolum} bölümüne eklendi."
            )
        )

        self.verileri_kaydet()

        return yeni_doktor["id"]

    def hasta_ara(self, arama_metni):

        arama_metni = (
            arama_metni.lower()
        )

        sonuclar = []

        for hasta in self.hastalar:

            bilgiler = (
                f"{hasta['ad_soyad']} "
                f"{hasta['tc']} "
                f"{hasta['telefon']} "
                f"{hasta['eposta']}"
            ).lower()

            if arama_metni in bilgiler:

                sonuclar.append(
                    hasta
                )

        return sonuclar

    def randevu_cakisma_var_mi(
        self,
        doktor_id,
        tarih,
        saat
    ):

        for randevu in self.randevular:

            if (
                randevu["doktor_id"] == doktor_id
                and randevu["tarih"] == tarih
                and randevu["saat"] == saat
                and randevu["durum"] == "AKTİF"
            ):

                return True

        return False

    def randevu_olustur(
        self,
        hasta_id,
        doktor_id,
        tarih,
        saat,
        sikayet
    ):

        hasta = self.hasta_bul(
            hasta_id
        )

        doktor = self.doktor_bul(
            doktor_id
        )

        if hasta is None:

            return (
                False,
                "Hasta bulunamadı."
            )

        if doktor is None:

            return (
                False,
                "Doktor bulunamadı."
            )

        if not hasta["aktif"]:

            return (
                False,
                "Pasif hasta için randevu oluşturulamaz."
            )

        if not doktor["aktif"]:

            return (
                False,
                "Pasif doktor için randevu oluşturulamaz."
            )

        if self.randevu_cakisma_var_mi(
            doktor_id,
            tarih,
            saat
        ):

            alarm_cal()

            seslendir(
                "Randevu çakışması algılandı."
            )

            return (
                False,
                (
                    "Doktorun aynı tarih ve saatte "
                    "başka bir randevusu bulunuyor."
                )
            )

        yeni_randevu = {
            "id": self.yeni_randevu_id_al(),
            "hasta_id": hasta_id,
            "hasta_adi": hasta["ad_soyad"],
            "doktor_id": doktor_id,
            "doktor_adi": doktor["ad_soyad"],
            "bolum": doktor["bolum"],
            "tarih": tarih,
            "saat": saat,
            "sikayet": sikayet,
            "durum": "AKTİF",
            "muayene_notu": None,
            "olusturma_tarihi": tarih_saat_al(),
            "guncelleme_tarihi": None
        }

        self.randevular.append(
            yeni_randevu
        )

        self.gecmis_kaydet(
            "RANDEVU OLUŞTURULDU",
            (
                f"{hasta['ad_soyad']} adlı hastaya "
                f"{doktor['ad_soyad']} için "
                f"{tarih} {saat} randevusu oluşturuldu."
            )
        )

        self.verileri_kaydet()

        return (
            True,
            yeni_randevu["id"]
        )

    def randevu_iptal_et(
        self,
        randevu_id
    ):

        randevu = self.randevu_bul(
            randevu_id
        )

        if randevu is None:

            return (
                False,
                "Randevu bulunamadı."
            )

        if randevu["durum"] == "İPTAL":

            return (
                False,
                "Randevu zaten iptal edilmiş."
            )

        if randevu["durum"] == "TAMAMLANDI":

            return (
                False,
                "Tamamlanmış randevu iptal edilemez."
            )

        randevu["durum"] = "İPTAL"
        randevu["guncelleme_tarihi"] = tarih_saat_al()

        self.gecmis_kaydet(
            "RANDEVU İPTAL EDİLDİ",
            (
                f"{randevu['hasta_adi']} adlı hastanın "
                f"{randevu['tarih']} tarihli "
                "randevusu iptal edildi."
            )
        )

        self.verileri_kaydet()

        return (
            True,
            "Randevu başarıyla iptal edildi."
        )

    def muayene_tamamla(
        self,
        randevu_id,
        muayene_notu
    ):

        randevu = self.randevu_bul(
            randevu_id
        )

        if randevu is None:

            return (
                False,
                "Randevu bulunamadı."
            )

        if randevu["durum"] == "İPTAL":

            return (
                False,
                "İptal edilmiş randevu tamamlanamaz."
            )

        if randevu["durum"] == "TAMAMLANDI":

            return (
                False,
                "Muayene zaten tamamlanmış."
            )

        randevu["durum"] = "TAMAMLANDI"
        randevu["muayene_notu"] = muayene_notu
        randevu["guncelleme_tarihi"] = tarih_saat_al()

        self.gecmis_kaydet(
            "MUAYENE TAMAMLANDI",
            (
                f"{randevu['hasta_adi']} adlı hastanın "
                f"{randevu['doktor_adi']} ile "
                "muayenesi tamamlandı."
            )
        )

        self.verileri_kaydet()

        return (
            True,
            "Muayene tamamlandı."
        )

    def gunluk_randevulari_getir(
        self,
        tarih
    ):

        return [
            randevu
            for randevu in self.randevular
            if randevu["tarih"] == tarih
        ]

    def hasta_randevularini_getir(
        self,
        hasta_id
    ):

        return [
            randevu
            for randevu in self.randevular
            if randevu["hasta_id"] == hasta_id
        ]

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

def hastalari_yazdir(
    hastalar,
    baslik
):

    if not hastalar:

        mesaj_yaz(
            "\nHasta kaydı bulunamadı."
        )

        return

    print("\n" + "=" * 78)
    print(f"{baslik:^78}")
    print("=" * 78)

    for hasta in hastalar:

        durum = (
            "AKTİF"
            if hasta["aktif"]
            else "PASİF"
        )

        print(
            f"\nHasta ID     : {hasta['id']}"
        )

        print(
            f"Ad soyad     : {hasta['ad_soyad']}"
        )

        print(
            f"TC           : {hasta['tc']}"
        )

        print(
            f"Telefon      : {hasta['telefon']}"
        )

        print(
            f"E-posta      : {hasta['eposta']}"
        )

        print(
            f"Durum        : {durum}"
        )

        print(
            f"Kayıt tarihi : {hasta['kayit_tarihi']}"
        )

        print("-" * 78)

    seslendir(
        f"Toplam {len(hastalar)} hasta gösterildi."
    )


def doktorlari_yazdir(
    doktorlar
):

    if not doktorlar:

        mesaj_yaz(
            "\nDoktor kaydı bulunamadı."
        )

        return

    print("\n" + "=" * 78)
    print(f"{'DOKTOR LİSTESİ':^78}")
    print("=" * 78)

    for doktor in doktorlar:

        durum = (
            "AKTİF"
            if doktor["aktif"]
            else "PASİF"
        )

        print(
            f"\nDoktor ID    : {doktor['id']}"
        )

        print(
            f"Ad soyad     : {doktor['ad_soyad']}"
        )

        print(
            f"Bölüm        : {doktor['bolum']}"
        )

        print(
            f"Telefon      : {doktor['telefon']}"
        )

        print(
            f"E-posta      : {doktor['eposta']}"
        )

        print(
            f"Durum        : {durum}"
        )

        print("-" * 78)

    seslendir(
        f"Toplam {len(doktorlar)} doktor gösterildi."
    )


def randevulari_yazdir(
    randevular,
    baslik
):

    if not randevular:

        mesaj_yaz(
            "\nRandevu kaydı bulunamadı."
        )

        return

    print("\n" + "=" * 85)
    print(f"{baslik:^85}")
    print("=" * 85)

    for randevu in randevular:

        print(
            f"\nRandevu ID      : {randevu['id']}"
        )

        print(
            f"Hasta            : {randevu['hasta_adi']}"
        )

        print(
            f"Doktor           : {randevu['doktor_adi']}"
        )

        print(
            f"Bölüm            : {randevu['bolum']}"
        )

        print(
            f"Tarih            : "
            f"{tarih_goster(randevu['tarih'])}"
        )

        print(
            f"Saat             : {randevu['saat']}"
        )

        print(
            f"Şikâyet          : {randevu['sikayet']}"
        )

        print(
            f"Durum            : {randevu['durum']}"
        )

        print(
            f"Muayene notu     : "
            f"{randevu['muayene_notu'] or '-'}"
        )

        print(
            f"Oluşturma tarihi : "
            f"{randevu['olusturma_tarihi']}"
        )

        print("-" * 85)

    seslendir(
        f"Toplam {len(randevular)} randevu gösterildi."
    )


def gecmisi_yazdir(
    islemler
):

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

class HastaneRandevuUygulamasi:

    def __init__(self):

        self.sistem = (
            HastaneYonetimSistemi()
        )

    @staticmethod
    def menuyu_goster():

        print("\n" + "=" * 66)
        print(
            "       48 - JSON HASTANE RANDEVU SİSTEMİ"
        )
        print("=" * 66)
        print("1  - Yeni hasta ekle            🔒")
        print("2  - Hastaları listele")
        print("3  - Hasta ara")
        print("4  - Yeni doktor ekle           🔒")
        print("5  - Doktorları listele")
        print("6  - Randevu oluştur            🔒")
        print("7  - Tüm randevuları göster")
        print("8  - Günlük randevuları göster")
        print("9  - Hasta randevu geçmişi")
        print("10 - Randevu iptal et           🔒")
        print("11 - Muayeneyi tamamla          🔒")
        print("12 - İşlem geçmişi              🔒")
        print("0  - Programı kapat")
        print("=" * 66)

    def baslat(self):

        mesaj_yaz(
            "\nJSON Hastane Randevu "
            "Sistemi başlatıldı."
        )

        while True:

            self.menuyu_goster()

            secim = input(
                "İşlem seçiniz: "
            ).strip()

            if secim == "1":
                self.hasta_ekle_menu()

            elif secim == "2":
                self.hastalari_listele_menu()

            elif secim == "3":
                self.hasta_ara_menu()

            elif secim == "4":
                self.doktor_ekle_menu()

            elif secim == "5":
                self.doktorlari_listele_menu()

            elif secim == "6":
                self.randevu_olustur_menu()

            elif secim == "7":
                self.tum_randevular_menu()

            elif secim == "8":
                self.gunluk_randevular_menu()

            elif secim == "9":
                self.hasta_randevu_gecmisi_menu()

            elif secim == "10":
                self.randevu_iptal_menu()

            elif secim == "11":
                self.muayene_tamamla_menu()

            elif secim == "12":
                self.gecmis_menu()

            elif secim == "0":

                mesaj_yaz(
                    "\nHastane randevu "
                    "sistemi kapatılıyor."
                )

                break

            else:

                sistemi_kapat(
                    "Geçersiz menü seçimi yapıldı."
                )

    def hasta_ekle_menu(self):

        yonetici_sifresi_dogrula()

        ad_soyad = input(
            "\nHasta ad soyad: "
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
                "Hasta bilgileri boş bırakılamaz."
            )

        if not tc.isdigit() or len(tc) != 11:

            sistemi_kapat(
                "TC kimlik numarası 11 rakam olmalıdır."
            )

        basarili, sonuc = (
            self.sistem.hasta_ekle(
                ad_soyad,
                tc,
                telefon,
                eposta
            )
        )

        if basarili:

            mesaj_yaz(
                f"\nHasta başarıyla eklendi. "
                f"Hasta numarası {sonuc}."
            )

        else:

            mesaj_yaz(
                f"\n{sonuc}"
            )

    def hastalari_listele_menu(self):

        hastalari_yazdir(
            self.sistem.hastalar,
            "HASTA LİSTESİ"
        )

    def hasta_ara_menu(self):

        arama_metni = input(
            "\nAranacak hasta: "
        ).strip()

        if not arama_metni:

            sistemi_kapat(
                "Arama metni boş bırakılamaz."
            )

        hastalari_yazdir(
            self.sistem.hasta_ara(
                arama_metni
            ),
            "ARAMA SONUÇLARI"
        )

    def doktor_ekle_menu(self):

        yonetici_sifresi_dogrula()

        ad_soyad = input(
            "\nDoktor ad soyad: "
        ).strip()

        bolum = input(
            "Bölüm: "
        ).strip()

        telefon = input(
            "Telefon: "
        ).strip()

        eposta = input(
            "E-posta: "
        ).strip().lower()

        if not all([
            ad_soyad,
            bolum,
            telefon,
            eposta
        ]):

            sistemi_kapat(
                "Doktor bilgileri boş bırakılamaz."
            )

        doktor_id = (
            self.sistem.doktor_ekle(
                ad_soyad,
                bolum,
                telefon,
                eposta
            )
        )

        mesaj_yaz(
            f"\nDoktor başarıyla eklendi. "
            f"Doktor numarası {doktor_id}."
        )

    def doktorlari_listele_menu(self):

        doktorlari_yazdir(
            self.sistem.doktorlar
        )

    def randevu_olustur_menu(self):

        yonetici_sifresi_dogrula()

        try:

            hasta_id = int(
                input(
                    "\nHasta ID: "
                )
            )

            doktor_id = int(
                input(
                    "Doktor ID: "
                )
            )

        except ValueError:

            sistemi_kapat(
                "Hasta veya doktor ID geçersiz."
            )

            return

        tarih = input(
            "Randevu tarihi (YYYY-AA-GG): "
        ).strip()

        saat = input(
            "Randevu saati (SS:DD): "
        ).strip()

        sikayet = input(
            "Hasta şikâyeti: "
        ).strip()

        if not tarih_saat_gecerli_mi(
            tarih,
            saat
        ):

            sistemi_kapat(
                "Randevu tarihi veya saati geçersiz."
            )

        if not sikayet:

            sistemi_kapat(
                "Hasta şikâyeti boş bırakılamaz."
            )

        basarili, sonuc = (
            self.sistem.randevu_olustur(
                hasta_id,
                doktor_id,
                tarih,
                saat,
                sikayet
            )
        )

        if basarili:

            mesaj_yaz(
                f"\nRandevu başarıyla oluşturuldu. "
                f"Randevu numarası {sonuc}."
            )

        else:

            mesaj_yaz(
                f"\n{sonuc}"
            )

    def tum_randevular_menu(self):

        randevulari_yazdir(
            self.sistem.randevular,
            "TÜM RANDEVULAR"
        )

    def gunluk_randevular_menu(self):

        tarih = input(
            "\nTarih giriniz "
            "(YYYY-AA-GG, bugün için boş): "
        ).strip()

        if not tarih:

            tarih = bugunun_tarihi()

        try:

            datetime.strptime(
                tarih,
                "%Y-%m-%d"
            )

        except ValueError:

            sistemi_kapat(
                "Tarih biçimi geçersiz."
            )

            return

        randevular = (
            self.sistem
            .gunluk_randevulari_getir(
                tarih
            )
        )

        randevulari_yazdir(
            randevular,
            (
                f"{tarih_goster(tarih)} "
                "TARİHLİ RANDEVULAR"
            )
        )

    def hasta_randevu_gecmisi_menu(self):

        try:

            hasta_id = int(
                input(
                    "\nHasta ID: "
                )
            )

        except ValueError:

            sistemi_kapat(
                "Hasta ID sayı olmalıdır."
            )

            return

        hasta = self.sistem.hasta_bul(
            hasta_id
        )

        if hasta is None:

            mesaj_yaz(
                "\nHasta bulunamadı."
            )

            return

        randevular = (
            self.sistem
            .hasta_randevularini_getir(
                hasta_id
            )
        )

        randevulari_yazdir(
            randevular,
            (
                f"{hasta['ad_soyad']} "
                "RANDEVU GEÇMİŞİ"
            )
        )

    def randevu_iptal_menu(self):

        yonetici_sifresi_dogrula()

        try:

            randevu_id = int(
                input(
                    "\nİptal edilecek randevu ID: "
                )
            )

        except ValueError:

            sistemi_kapat(
                "Randevu ID sayı olmalıdır."
            )

            return

        _, mesaj = (
            self.sistem.randevu_iptal_et(
                randevu_id
            )
        )

        mesaj_yaz(
            f"\n{mesaj}"
        )

    def muayene_tamamla_menu(self):

        yonetici_sifresi_dogrula()

        try:

            randevu_id = int(
                input(
                    "\nTamamlanacak randevu ID: "
                )
            )

        except ValueError:

            sistemi_kapat(
                "Randevu ID sayı olmalıdır."
            )

            return

        muayene_notu = input(
            "Muayene notu: "
        ).strip()

        if not muayene_notu:

            sistemi_kapat(
                "Muayene notu boş bırakılamaz."
            )

        _, mesaj = (
            self.sistem.muayene_tamamla(
                randevu_id,
                muayene_notu
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
            HastaneRandevuUygulamasi()
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