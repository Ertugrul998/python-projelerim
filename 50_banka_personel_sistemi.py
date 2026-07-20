import sqlite3
import hashlib
import getpass
import subprocess
from datetime import datetime
from decimal import Decimal, InvalidOperation


VERITABANI_ADI = "banka_personel.db"
MAKSIMUM_GIRIS_DENEMESI = 3


# =========================================================
# SESLİ YANIT
# =========================================================

def seslendir(metin):
    """
    macOS say komutuyla sesli yanıt verir.
    """

    try:
        subprocess.run(
            ["say", str(metin)],
            check=False
        )

    except FileNotFoundError:
        pass


# =========================================================
# YARDIMCI FONKSİYONLAR
# =========================================================

def tarih_saat():
    return datetime.now().strftime(
        "%d.%m.%Y %H:%M:%S"
    )


def sifre_hashle(sifre):
    return hashlib.sha256(
        sifre.encode("utf-8")
    ).hexdigest()


def para_formatla(kurus):
    """
    Veritabanındaki kuruş değerini TL formatına çevirir.
    """

    tl = Decimal(kurus) / Decimal("100")

    metin = f"{tl:,.2f}"

    metin = metin.replace(",", "X")
    metin = metin.replace(".", ",")
    metin = metin.replace("X", ".")

    return f"{metin} TL"


def para_al(mesaj):
    """
    Kullanıcıdan güvenli şekilde para miktarı alır.
    Sonucu kuruş olarak tam sayı döndürür.
    """

    while True:

        veri = input(mesaj).strip()

        veri = veri.replace(".", "")
        veri = veri.replace(",", ".")

        try:

            tutar = Decimal(veri)

            if tutar <= 0:

                print(
                    "Tutar sıfırdan büyük olmalıdır."
                )

                seslendir(
                    "Tutar sıfırdan büyük olmalıdır."
                )

                continue

            tutar = tutar.quantize(
                Decimal("0.01")
            )

            kurus = int(
                tutar * Decimal("100")
            )

            return kurus

        except InvalidOperation:

            print(
                "Geçerli bir para tutarı giriniz."
            )

            seslendir(
                "Geçersiz para tutarı."
            )


def devam_et():
    input(
        "\nDevam etmek için Enter'a basınız..."
    )


# =========================================================
# VERİTABANI SINIFI
# =========================================================

class BankaVeritabani:

    def __init__(self):

        self.baglanti = sqlite3.connect(
            VERITABANI_ADI
        )

        self.baglanti.row_factory = sqlite3.Row

        self.imlec = self.baglanti.cursor()

        self.tablolari_olustur()

        self.varsayilan_personeli_olustur()

    # -----------------------------------------------------
    # TABLOLARI OLUŞTUR
    # -----------------------------------------------------

    def tablolari_olustur(self):

        self.imlec.execute(
            """
            CREATE TABLE IF NOT EXISTS personeller (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_adi TEXT UNIQUE NOT NULL,
                sifre_hash TEXT NOT NULL,
                ad_soyad TEXT NOT NULL,
                yetki TEXT NOT NULL,
                aktif INTEGER NOT NULL DEFAULT 1
            )
            """
        )

        self.imlec.execute(
            """
            CREATE TABLE IF NOT EXISTS musteriler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tc_no TEXT UNIQUE NOT NULL,
                ad TEXT NOT NULL,
                soyad TEXT NOT NULL,
                telefon TEXT,
                adres TEXT,
                kayit_tarihi TEXT NOT NULL
            )
            """
        )

        self.imlec.execute(
            """
            CREATE TABLE IF NOT EXISTS hesaplar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hesap_no TEXT UNIQUE NOT NULL,
                musteri_id INTEGER NOT NULL,
                hesap_turu TEXT NOT NULL,
                bakiye_kurus INTEGER NOT NULL DEFAULT 0,
                durum TEXT NOT NULL DEFAULT 'AKTIF',
                acilis_tarihi TEXT NOT NULL,

                FOREIGN KEY (musteri_id)
                REFERENCES musteriler(id)
            )
            """
        )

        self.imlec.execute(
            """
            CREATE TABLE IF NOT EXISTS islemler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hesap_no TEXT NOT NULL,
                hedef_hesap_no TEXT,
                islem_turu TEXT NOT NULL,
                tutar_kurus INTEGER NOT NULL,
                onceki_bakiye_kurus INTEGER NOT NULL,
                sonraki_bakiye_kurus INTEGER NOT NULL,
                personel_adi TEXT NOT NULL,
                aciklama TEXT,
                tarih TEXT NOT NULL
            )
            """
        )

        self.imlec.execute(
            """
            CREATE TABLE IF NOT EXISTS personel_girisleri (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_adi TEXT NOT NULL,
                durum TEXT NOT NULL,
                tarih TEXT NOT NULL
            )
            """
        )

        self.baglanti.commit()

    # -----------------------------------------------------
    # VARSAYILAN PERSONEL
    # -----------------------------------------------------

    def varsayilan_personeli_olustur(self):

        kullanici_adi = "admin"
        sifre = "2580"

        self.imlec.execute(
            """
            SELECT id
            FROM personeller
            WHERE kullanici_adi = ?
            """,
            (
                kullanici_adi,
            )
        )

        personel = self.imlec.fetchone()

        if personel is None:

            self.imlec.execute(
                """
                INSERT INTO personeller (
                    kullanici_adi,
                    sifre_hash,
                    ad_soyad,
                    yetki,
                    aktif
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    kullanici_adi,
                    sifre_hashle(sifre),
                    "Sistem Yöneticisi",
                    "YONETICI",
                    1
                )
            )

            self.baglanti.commit()

    # -----------------------------------------------------
    # PERSONEL GİRİŞ KAYDI
    # -----------------------------------------------------

    def giris_kaydi_ekle(
        self,
        kullanici_adi,
        durum
    ):

        self.imlec.execute(
            """
            INSERT INTO personel_girisleri (
                kullanici_adi,
                durum,
                tarih
            )
            VALUES (?, ?, ?)
            """,
            (
                kullanici_adi,
                durum,
                tarih_saat()
            )
        )

        self.baglanti.commit()

    # -----------------------------------------------------
    # PERSONEL DOĞRULAMA
    # -----------------------------------------------------

    def personel_dogrula(
        self,
        kullanici_adi,
        sifre
    ):

        self.imlec.execute(
            """
            SELECT *
            FROM personeller
            WHERE kullanici_adi = ?
            AND sifre_hash = ?
            AND aktif = 1
            """,
            (
                kullanici_adi,
                sifre_hashle(sifre)
            )
        )

        return self.imlec.fetchone()

    # -----------------------------------------------------
    # YENİ MÜŞTERİ VE HESAP OLUŞTUR
    # -----------------------------------------------------

    def musteri_ekle(
        self,
        tc_no,
        ad,
        soyad,
        telefon,
        adres,
        hesap_no,
        hesap_turu
    ):

        try:

            self.imlec.execute(
                """
                INSERT INTO musteriler (
                    tc_no,
                    ad,
                    soyad,
                    telefon,
                    adres,
                    kayit_tarihi
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    tc_no,
                    ad,
                    soyad,
                    telefon,
                    adres,
                    tarih_saat()
                )
            )

            musteri_id = self.imlec.lastrowid

            self.imlec.execute(
                """
                INSERT INTO hesaplar (
                    hesap_no,
                    musteri_id,
                    hesap_turu,
                    bakiye_kurus,
                    durum,
                    acilis_tarihi
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    hesap_no,
                    musteri_id,
                    hesap_turu,
                    0,
                    "AKTIF",
                    tarih_saat()
                )
            )

            self.baglanti.commit()

            print(
                "\nMüşteri ve banka hesabı oluşturuldu."
            )

            print(
                f"Hesap numarası: {hesap_no}"
            )

            seslendir(
                "Müşteri ve banka hesabı oluşturuldu."
            )

        except sqlite3.IntegrityError:

            self.baglanti.rollback()

            print(
                "\nBu TC kimlik numarası veya hesap numarası "
                "zaten kayıtlıdır."
            )

            seslendir(
                "Bu müşteri veya hesap zaten kayıtlıdır."
            )

    # -----------------------------------------------------
    # MÜŞTERİ ARA
    # -----------------------------------------------------

    def musteri_ara(self, arama):

        self.imlec.execute(
            """
            SELECT
                musteriler.id,
                musteriler.tc_no,
                musteriler.ad,
                musteriler.soyad,
                musteriler.telefon,
                musteriler.adres,
                musteriler.kayit_tarihi,
                hesaplar.hesap_no,
                hesaplar.hesap_turu,
                hesaplar.bakiye_kurus,
                hesaplar.durum,
                hesaplar.acilis_tarihi

            FROM musteriler

            INNER JOIN hesaplar
            ON musteriler.id = hesaplar.musteri_id

            WHERE musteriler.tc_no = ?
            OR hesaplar.hesap_no = ?
            """,
            (
                arama,
                arama
            )
        )

        sonuc = self.imlec.fetchone()

        if sonuc is None:

            print(
                "\nMüşteri bulunamadı."
            )

            seslendir(
                "Müşteri bulunamadı."
            )

            return None

        print(
            "\n======================================"
        )

        print(
            "          MÜŞTERİ BİLGİLERİ"
        )

        print(
            "======================================"
        )

        print(
            f"TC Kimlik No : {sonuc['tc_no']}"
        )

        print(
            f"Ad Soyad     : "
            f"{sonuc['ad']} {sonuc['soyad']}"
        )

        print(
            f"Telefon      : {sonuc['telefon']}"
        )

        print(
            f"Adres        : {sonuc['adres']}"
        )

        print(
            f"Hesap No     : {sonuc['hesap_no']}"
        )

        print(
            f"Hesap Türü   : {sonuc['hesap_turu']}"
        )

        print(
            f"Bakiye       : "
            f"{para_formatla(sonuc['bakiye_kurus'])}"
        )

        print(
            f"Hesap Durumu : {sonuc['durum']}"
        )

        print(
            f"Kayıt Tarihi : {sonuc['kayit_tarihi']}"
        )

        print(
            "======================================"
        )

        seslendir(
            "Müşteri bulundu."
        )

        return sonuc

    # -----------------------------------------------------
    # MÜŞTERİLERİ LİSTELE
    # -----------------------------------------------------

    def musterileri_listele(self):

        self.imlec.execute(
            """
            SELECT
                musteriler.tc_no,
                musteriler.ad,
                musteriler.soyad,
                hesaplar.hesap_no,
                hesaplar.hesap_turu,
                hesaplar.bakiye_kurus,
                hesaplar.durum

            FROM musteriler

            INNER JOIN hesaplar
            ON musteriler.id = hesaplar.musteri_id

            ORDER BY musteriler.ad, musteriler.soyad
            """
        )

        musteriler = self.imlec.fetchall()

        if not musteriler:

            print(
                "\nKayıtlı müşteri bulunmamaktadır."
            )

            seslendir(
                "Kayıtlı müşteri bulunmamaktadır."
            )

            return

        print(
            "\n=========================================================================="
        )

        print(
            "                         MÜŞTERİ LİSTESİ"
        )

        print(
            "=========================================================================="
        )

        print(
            f"{'TC NO':<13}"
            f"{'AD SOYAD':<25}"
            f"{'HESAP NO':<15}"
            f"{'BAKİYE':>15}"
        )

        print(
            "-" * 68
        )

        for musteri in musteriler:

            ad_soyad = (
                f"{musteri['ad']} "
                f"{musteri['soyad']}"
            )

            print(
                f"{musteri['tc_no']:<13}"
                f"{ad_soyad:<25}"
                f"{musteri['hesap_no']:<15}"
                f"{para_formatla(musteri['bakiye_kurus']):>15}"
            )

        print(
            "=========================================================================="
        )

    # -----------------------------------------------------
    # HESAP BUL
    # -----------------------------------------------------

    def hesap_bul(self, hesap_no):

        self.imlec.execute(
            """
            SELECT
                hesaplar.*,
                musteriler.ad,
                musteriler.soyad

            FROM hesaplar

            INNER JOIN musteriler
            ON hesaplar.musteri_id = musteriler.id

            WHERE hesaplar.hesap_no = ?
            """,
            (
                hesap_no,
            )
        )

        return self.imlec.fetchone()

    # -----------------------------------------------------
    # İŞLEM KAYDI
    # -----------------------------------------------------

    def islem_kaydi_ekle(
        self,
        hesap_no,
        hedef_hesap_no,
        islem_turu,
        tutar_kurus,
        onceki_bakiye_kurus,
        sonraki_bakiye_kurus,
        personel_adi,
        aciklama
    ):

        self.imlec.execute(
            """
            INSERT INTO islemler (
                hesap_no,
                hedef_hesap_no,
                islem_turu,
                tutar_kurus,
                onceki_bakiye_kurus,
                sonraki_bakiye_kurus,
                personel_adi,
                aciklama,
                tarih
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                hesap_no,
                hedef_hesap_no,
                islem_turu,
                tutar_kurus,
                onceki_bakiye_kurus,
                sonraki_bakiye_kurus,
                personel_adi,
                aciklama,
                tarih_saat()
            )
        )

    # -----------------------------------------------------
    # PARA YATIR
    # -----------------------------------------------------

    def para_yatir(
        self,
        hesap_no,
        tutar_kurus,
        personel_adi
    ):

        hesap = self.hesap_bul(
            hesap_no
        )

        if hesap is None:

            print(
                "\nHesap bulunamadı."
            )

            seslendir(
                "Hesap bulunamadı."
            )

            return

        if hesap["durum"] != "AKTIF":

            print(
                "\nBu hesap aktif değildir."
            )

            seslendir(
                "Bu hesap aktif değildir."
            )

            return

        onceki_bakiye = hesap[
            "bakiye_kurus"
        ]

        sonraki_bakiye = (
            onceki_bakiye + tutar_kurus
        )

        try:

            self.imlec.execute(
                """
                UPDATE hesaplar
                SET bakiye_kurus = ?
                WHERE hesap_no = ?
                """,
                (
                    sonraki_bakiye,
                    hesap_no
                )
            )

            self.islem_kaydi_ekle(
                hesap_no=hesap_no,
                hedef_hesap_no=None,
                islem_turu="PARA YATIRMA",
                tutar_kurus=tutar_kurus,
                onceki_bakiye_kurus=onceki_bakiye,
                sonraki_bakiye_kurus=sonraki_bakiye,
                personel_adi=personel_adi,
                aciklama="Şube personeli tarafından para yatırıldı."
            )

            self.baglanti.commit()

            print(
                "\nPara yatırma işlemi başarılı."
            )

            print(
                f"Yatırılan tutar : "
                f"{para_formatla(tutar_kurus)}"
            )

            print(
                f"Yeni bakiye     : "
                f"{para_formatla(sonraki_bakiye)}"
            )

            seslendir(
                "Para yatırma işlemi başarılı."
            )

        except sqlite3.Error:

            self.baglanti.rollback()

            print(
                "\nPara yatırma işlemi sırasında hata oluştu."
            )

            seslendir(
                "İşlem gerçekleştirilemedi."
            )

    # -----------------------------------------------------
    # PARA ÇEK
    # -----------------------------------------------------

    def para_cek(
        self,
        hesap_no,
        tutar_kurus,
        personel_adi
    ):

        hesap = self.hesap_bul(
            hesap_no
        )

        if hesap is None:

            print(
                "\nHesap bulunamadı."
            )

            seslendir(
                "Hesap bulunamadı."
            )

            return

        if hesap["durum"] != "AKTIF":

            print(
                "\nBu hesap aktif değildir."
            )

            seslendir(
                "Bu hesap aktif değildir."
            )

            return

        onceki_bakiye = hesap[
            "bakiye_kurus"
        ]

        if tutar_kurus > onceki_bakiye:

            print(
                "\nYetersiz bakiye."
            )

            print(
                f"Mevcut bakiye: "
                f"{para_formatla(onceki_bakiye)}"
            )

            seslendir(
                "Yetersiz bakiye."
            )

            return

        sonraki_bakiye = (
            onceki_bakiye - tutar_kurus
        )

        try:

            self.imlec.execute(
                """
                UPDATE hesaplar
                SET bakiye_kurus = ?
                WHERE hesap_no = ?
                """,
                (
                    sonraki_bakiye,
                    hesap_no
                )
            )

            self.islem_kaydi_ekle(
                hesap_no=hesap_no,
                hedef_hesap_no=None,
                islem_turu="PARA ÇEKME",
                tutar_kurus=tutar_kurus,
                onceki_bakiye_kurus=onceki_bakiye,
                sonraki_bakiye_kurus=sonraki_bakiye,
                personel_adi=personel_adi,
                aciklama="Şube personeli tarafından para çekildi."
            )

            self.baglanti.commit()

            print(
                "\nPara çekme işlemi başarılı."
            )

            print(
                f"Çekilen tutar : "
                f"{para_formatla(tutar_kurus)}"
            )

            print(
                f"Yeni bakiye   : "
                f"{para_formatla(sonraki_bakiye)}"
            )

            seslendir(
                "Para çekme işlemi başarılı."
            )

        except sqlite3.Error:

            self.baglanti.rollback()

            print(
                "\nPara çekme işlemi sırasında hata oluştu."
            )

            seslendir(
                "İşlem gerçekleştirilemedi."
            )

    # -----------------------------------------------------
    # HAVALE
    # -----------------------------------------------------

    def havale_yap(
        self,
        gonderen_hesap_no,
        alici_hesap_no,
        tutar_kurus,
        personel_adi
    ):

        if gonderen_hesap_no == alici_hesap_no:

            print(
                "\nGönderen ve alıcı hesap aynı olamaz."
            )

            seslendir(
                "Gönderen ve alıcı hesap aynı olamaz."
            )

            return

        gonderen = self.hesap_bul(
            gonderen_hesap_no
        )

        alici = self.hesap_bul(
            alici_hesap_no
        )

        if gonderen is None:

            print(
                "\nGönderen hesap bulunamadı."
            )

            seslendir(
                "Gönderen hesap bulunamadı."
            )

            return

        if alici is None:

            print(
                "\nAlıcı hesap bulunamadı."
            )

            seslendir(
                "Alıcı hesap bulunamadı."
            )

            return

        if (
            gonderen["durum"] != "AKTIF"
            or alici["durum"] != "AKTIF"
        ):

            print(
                "\nHesaplardan biri aktif değildir."
            )

            seslendir(
                "Hesaplardan biri aktif değildir."
            )

            return

        gonderen_onceki = gonderen[
            "bakiye_kurus"
        ]

        alici_onceki = alici[
            "bakiye_kurus"
        ]

        if tutar_kurus > gonderen_onceki:

            print(
                "\nGönderen hesapta yeterli bakiye yok."
            )

            seslendir(
                "Yetersiz bakiye."
            )

            return

        gonderen_sonraki = (
            gonderen_onceki - tutar_kurus
        )

        alici_sonraki = (
            alici_onceki + tutar_kurus
        )

        try:

            self.imlec.execute(
                """
                UPDATE hesaplar
                SET bakiye_kurus = ?
                WHERE hesap_no = ?
                """,
                (
                    gonderen_sonraki,
                    gonderen_hesap_no
                )
            )

            self.imlec.execute(
                """
                UPDATE hesaplar
                SET bakiye_kurus = ?
                WHERE hesap_no = ?
                """,
                (
                    alici_sonraki,
                    alici_hesap_no
                )
            )

            self.islem_kaydi_ekle(
                hesap_no=gonderen_hesap_no,
                hedef_hesap_no=alici_hesap_no,
                islem_turu="HAVALE GÖNDERİMİ",
                tutar_kurus=tutar_kurus,
                onceki_bakiye_kurus=gonderen_onceki,
                sonraki_bakiye_kurus=gonderen_sonraki,
                personel_adi=personel_adi,
                aciklama="Hesaptan havale gönderildi."
            )

            self.islem_kaydi_ekle(
                hesap_no=alici_hesap_no,
                hedef_hesap_no=gonderen_hesap_no,
                islem_turu="HAVALE ALIMI",
                tutar_kurus=tutar_kurus,
                onceki_bakiye_kurus=alici_onceki,
                sonraki_bakiye_kurus=alici_sonraki,
                personel_adi=personel_adi,
                aciklama="Hesaba havale geldi."
            )

            self.baglanti.commit()

            print(
                "\nHavale işlemi başarılı."
            )

            print(
                f"Gönderilen tutar : "
                f"{para_formatla(tutar_kurus)}"
            )

            print(
                f"Gönderen bakiye  : "
                f"{para_formatla(gonderen_sonraki)}"
            )

            seslendir(
                "Havale işlemi başarılı."
            )

        except sqlite3.Error:

            self.baglanti.rollback()

            print(
                "\nHavale işlemi sırasında hata oluştu."
            )

            seslendir(
                "Havale gerçekleştirilemedi."
            )

    # -----------------------------------------------------
    # BAKİYE GÖRÜNTÜLE
    # -----------------------------------------------------

    def bakiye_goruntule(self, hesap_no):

        hesap = self.hesap_bul(
            hesap_no
        )

        if hesap is None:

            print(
                "\nHesap bulunamadı."
            )

            seslendir(
                "Hesap bulunamadı."
            )

            return

        print(
            "\n======================================"
        )

        print(
            "             HESAP BİLGİSİ"
        )

        print(
            "======================================"
        )

        print(
            f"Müşteri  : "
            f"{hesap['ad']} {hesap['soyad']}"
        )

        print(
            f"Hesap No : {hesap['hesap_no']}"
        )

        print(
            f"Hesap Türü: {hesap['hesap_turu']}"
        )

        print(
            f"Bakiye   : "
            f"{para_formatla(hesap['bakiye_kurus'])}"
        )

        print(
            f"Durum    : {hesap['durum']}"
        )

        print(
            "======================================"
        )

        seslendir(
            f"Hesap bakiyesi "
            f"{hesap['bakiye_kurus'] / 100:.2f} liradır."
        )

    # -----------------------------------------------------
    # İŞLEM GEÇMİŞİ
    # -----------------------------------------------------

    def islem_gecmisi(
        self,
        hesap_no
    ):

        hesap = self.hesap_bul(
            hesap_no
        )

        if hesap is None:

            print(
                "\nHesap bulunamadı."
            )

            seslendir(
                "Hesap bulunamadı."
            )

            return

        self.imlec.execute(
            """
            SELECT *
            FROM islemler
            WHERE hesap_no = ?
            ORDER BY id DESC
            """,
            (
                hesap_no,
            )
        )

        islemler = self.imlec.fetchall()

        if not islemler:

            print(
                "\nBu hesaba ait işlem bulunmamaktadır."
            )

            seslendir(
                "İşlem geçmişi bulunmamaktadır."
            )

            return

        print(
            "\n=============================================================="
        )

        print(
            f"İŞLEM GEÇMİŞİ — {hesap_no}"
        )

        print(
            "=============================================================="
        )

        for islem in islemler:

            print(
                f"\nİşlem No      : {islem['id']}"
            )

            print(
                f"İşlem Türü    : {islem['islem_turu']}"
            )

            print(
                f"Tutar          : "
                f"{para_formatla(islem['tutar_kurus'])}"
            )

            print(
                f"Önceki Bakiye : "
                f"{para_formatla(islem['onceki_bakiye_kurus'])}"
            )

            print(
                f"Sonraki Bakiye: "
                f"{para_formatla(islem['sonraki_bakiye_kurus'])}"
            )

            if islem["hedef_hesap_no"]:

                print(
                    f"Diğer Hesap   : "
                    f"{islem['hedef_hesap_no']}"
                )

            print(
                f"Personel      : {islem['personel_adi']}"
            )

            print(
                f"Tarih         : {islem['tarih']}"
            )

            print(
                f"Açıklama      : {islem['aciklama']}"
            )

            print(
                "-" * 62
            )

    # -----------------------------------------------------
    # GÜN SONU / BANKA ÖZETİ
    # -----------------------------------------------------

    def banka_ozeti(self):

        self.imlec.execute(
            """
            SELECT COUNT(*) AS musteri_sayisi
            FROM musteriler
            """
        )

        musteri_sayisi = self.imlec.fetchone()[
            "musteri_sayisi"
        ]

        self.imlec.execute(
            """
            SELECT COUNT(*) AS hesap_sayisi
            FROM hesaplar
            """
        )

        hesap_sayisi = self.imlec.fetchone()[
            "hesap_sayisi"
        ]

        self.imlec.execute(
            """
            SELECT
                COALESCE(
                    SUM(bakiye_kurus),
                    0
                ) AS toplam_bakiye
            FROM hesaplar
            """
        )

        toplam_bakiye = self.imlec.fetchone()[
            "toplam_bakiye"
        ]

        self.imlec.execute(
            """
            SELECT COUNT(*) AS islem_sayisi
            FROM islemler
            """
        )

        islem_sayisi = self.imlec.fetchone()[
            "islem_sayisi"
        ]

        print(
            "\n======================================"
        )

        print(
            "             BANKA ÖZETİ"
        )

        print(
            "======================================"
        )

        print(
            f"Toplam müşteri : {musteri_sayisi}"
        )

        print(
            f"Toplam hesap   : {hesap_sayisi}"
        )

        print(
            f"Toplam işlem   : {islem_sayisi}"
        )

        print(
            f"Toplam mevduat : "
            f"{para_formatla(toplam_bakiye)}"
        )

        print(
            "======================================"
        )

        seslendir(
            "Banka özeti görüntülendi."
        )

    # -----------------------------------------------------
    # VERİTABANINI KAPAT
    # -----------------------------------------------------

    def kapat(self):

        self.baglanti.close()


# =========================================================
# BANKA PERSONEL UYGULAMASI
# =========================================================

class BankaPersonelUygulamasi:

    def __init__(self):

        self.veritabani = BankaVeritabani()

        self.aktif_personel = None

    # -----------------------------------------------------
    # PERSONEL GİRİŞİ
    # -----------------------------------------------------

    def personel_girisi(self):

        print(
            "\n======================================"
        )

        print(
            "       BANKA PERSONEL GİRİŞİ"
        )

        print(
            "======================================"
        )

        for deneme in range(
            1,
            MAKSIMUM_GIRIS_DENEMESI + 1
        ):

            kullanici_adi = input(
                "Kullanıcı adı: "
            ).strip()

            sifre = getpass.getpass(
                "Personel şifresi: "
            )

            personel = (
                self.veritabani.personel_dogrula(
                    kullanici_adi,
                    sifre
                )
            )

            if personel:

                self.aktif_personel = personel

                self.veritabani.giris_kaydi_ekle(
                    kullanici_adi,
                    "BASARILI"
                )

                print(
                    "\nPersonel girişi başarılı."
                )

                print(
                    f"Hoş geldiniz, "
                    f"{personel['ad_soyad']}."
                )

                seslendir(
                    "Personel girişi başarılı. "
                    f"Hoş geldiniz "
                    f"{personel['ad_soyad']}."
                )

                return True

            kalan = (
                MAKSIMUM_GIRIS_DENEMESI - deneme
            )

            self.veritabani.giris_kaydi_ekle(
                kullanici_adi,
                "BASARISIZ"
            )

            print(
                "\nKullanıcı adı veya şifre hatalı."
            )

            if kalan > 0:

                print(
                    f"Kalan deneme hakkı: {kalan}"
                )

                seslendir(
                    "Kullanıcı adı veya şifre hatalı."
                )

        print(
            "\nÜç kez hatalı giriş yapıldı."
        )

        print(
            "Güvenlik nedeniyle sistem kapatılıyor."
        )

        seslendir(
            "Üç kez hatalı giriş yapıldı. "
            "Güvenlik nedeniyle sistem kapatılıyor."
        )

        return False

    # -----------------------------------------------------
    # MÜŞTERİ EKLEME EKRANI
    # -----------------------------------------------------

    def musteri_ekleme_ekrani(self):

        print(
            "\n--- YENİ MÜŞTERİ VE HESAP OLUŞTUR ---"
        )

        tc_no = input(
            "TC Kimlik No: "
        ).strip()

        if not (
            tc_no.isdigit()
            and len(tc_no) == 11
        ):

            print(
                "TC kimlik numarası 11 rakam olmalıdır."
            )

            seslendir(
                "Geçersiz TC kimlik numarası."
            )

            return

        ad = input(
            "Ad: "
        ).strip().title()

        soyad = input(
            "Soyad: "
        ).strip().upper()

        telefon = input(
            "Telefon: "
        ).strip()

        adres = input(
            "Adres: "
        ).strip()

        hesap_no = input(
            "Hesap Numarası: "
        ).strip()

        print(
            "\n1 - Vadesiz Hesap"
        )

        print(
            "2 - Vadeli Hesap"
        )

        hesap_secimi = input(
            "Hesap türü: "
        ).strip()

        if hesap_secimi == "1":

            hesap_turu = "VADESIZ"

        elif hesap_secimi == "2":

            hesap_turu = "VADELI"

        else:

            print(
                "Geçersiz hesap türü."
            )

            seslendir(
                "Geçersiz hesap türü."
            )

            return

        if not ad or not soyad or not hesap_no:

            print(
                "Ad, soyad ve hesap numarası boş bırakılamaz."
            )

            seslendir(
                "Eksik müşteri bilgisi."
            )

            return

        self.veritabani.musteri_ekle(
            tc_no,
            ad,
            soyad,
            telefon,
            adres,
            hesap_no,
            hesap_turu
        )

    # -----------------------------------------------------
    # ANA MENÜ
    # -----------------------------------------------------

    def ana_menu(self):

        while True:

            print(
                """
==================================================
          BANKA PERSONEL İŞLEM SİSTEMİ
==================================================

1  - Yeni Müşteri ve Hesap Oluştur
2  - Müşteri Ara
3  - Müşterileri Listele
4  - Para Yatır
5  - Para Çek
6  - Havale Yap
7  - Bakiye Görüntüle
8  - İşlem Geçmişi
9  - Banka Özeti
10 - Güvenli Çıkış

==================================================
"""
            )

            secim = input(
                "İşlem seçiniz: "
            ).strip()

            if secim == "1":

                self.musteri_ekleme_ekrani()

                devam_et()

            elif secim == "2":

                arama = input(
                    "TC veya hesap numarası: "
                ).strip()

                self.veritabani.musteri_ara(
                    arama
                )

                devam_et()

            elif secim == "3":

                self.veritabani.musterileri_listele()

                devam_et()

            elif secim == "4":

                hesap_no = input(
                    "Hesap numarası: "
                ).strip()

                tutar = para_al(
                    "Yatırılacak tutar: "
                )

                self.veritabani.para_yatir(
                    hesap_no,
                    tutar,
                    self.aktif_personel["ad_soyad"]
                )

                devam_et()

            elif secim == "5":

                hesap_no = input(
                    "Hesap numarası: "
                ).strip()

                tutar = para_al(
                    "Çekilecek tutar: "
                )

                self.veritabani.para_cek(
                    hesap_no,
                    tutar,
                    self.aktif_personel["ad_soyad"]
                )

                devam_et()

            elif secim == "6":

                gonderen = input(
                    "Gönderen hesap numarası: "
                ).strip()

                alici = input(
                    "Alıcı hesap numarası: "
                ).strip()

                tutar = para_al(
                    "Havale tutarı: "
                )

                self.veritabani.havale_yap(
                    gonderen,
                    alici,
                    tutar,
                    self.aktif_personel["ad_soyad"]
                )

                devam_et()

            elif secim == "7":

                hesap_no = input(
                    "Hesap numarası: "
                ).strip()

                self.veritabani.bakiye_goruntule(
                    hesap_no
                )

                devam_et()

            elif secim == "8":

                hesap_no = input(
                    "Hesap numarası: "
                ).strip()

                self.veritabani.islem_gecmisi(
                    hesap_no
                )

                devam_et()

            elif secim == "9":

                self.veritabani.banka_ozeti()

                devam_et()

            elif secim == "10":

                print(
                    "\nPersonel oturumu kapatıldı."
                )

                print(
                    "Banka sistemi güvenli şekilde kapatılıyor."
                )

                seslendir(
                    "Personel oturumu kapatıldı. "
                    "Banka sistemi güvenli şekilde kapatılıyor."
                )

                break

            else:

                print(
                    "\nGeçersiz menü seçimi."
                )

                seslendir(
                    "Geçersiz menü seçimi."
                )

                devam_et()

    # -----------------------------------------------------
    # PROGRAMI BAŞLAT
    # -----------------------------------------------------

    def baslat(self):

        try:

            if self.personel_girisi():

                self.ana_menu()

        except KeyboardInterrupt:

            print(
                "\n\nProgram kullanıcı tarafından durduruldu."
            )

            seslendir(
                "Program kullanıcı tarafından durduruldu."
            )

        except sqlite3.Error as hata:

            print(
                f"\nVeritabanı hatası: {hata}"
            )

            seslendir(
                "Kritik veritabanı hatası oluştu."
            )

        except Exception as hata:

            print(
                f"\nBeklenmeyen hata: {hata}"
            )

            seslendir(
                "Beklenmeyen bir sistem hatası oluştu."
            )

        finally:

            self.veritabani.kapat()

            print(
                "\nVeritabanı bağlantısı kapatıldı."
            )


# =========================================================
# PROGRAM BAŞLANGICI
# =========================================================

if __name__ == "__main__":

    uygulama = BankaPersonelUygulamasi()

    uygulama.baslat()