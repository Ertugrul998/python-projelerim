# Proje 24 - Kullanıcı Kayıt ve Giriş sistemi
# Sürüm 1.0

kullanici_adi = input("Kullanıcı adı giriniz: ")
sifre = input("Şifre giriniz: ")

with open("kullanicilar.txt", "r", encoding="utf-8") as dosya:
    for satir in dosya:
        kayitli_ad, kayitli_sifre = satir.strip().split(",")

        if kullanici_adi == kayitli_ad:
            kullanici_var = True
            break

if kullanici_var:
    print("Bu kullanıcı adı zaten kayıtlı!")
else:
    with open("kullanicilar.txt", "a", encoding="utf-8") as dosya:
        dosya.write(kullanici_adi + "," + sifre + "\n")

    print("Kullanıcı kaydedildi")

giris_adi = input("Giriş için kullanıcı adını giriniz: ")
giris_sifre = input("Giriş için şifrenizi giriniz: ")

giris_basarili = False

with open("kullanicilar.txt", "r", encoding="utf-8") as dosya:
    for satir in dosya:
        kayitli_ad, kayitli_sifre = satir.strip().split(",")

        if giris_adi == kayitli_ad and giris_sifre == kayitli_sifre:
            giris_basarili = True
            break

if giris_basarili:
    print("Giriş başarılı.")
else:
    print("Kullanıcı adı veya şifre hatalı.")



