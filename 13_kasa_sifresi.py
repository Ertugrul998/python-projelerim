dogru_sifre = "2580"
kalan_hak = 3

print("--- KASA ŞİFRE SİSTEMİ ---")

while kalan_hak > 0:

    girilen_sifre = input("Kasa şifresini girin: ")

    if girilen_sifre == dogru_sifre:
        print("✅ Şifre doğru.")
        print("🔓 Kasa açıldı.")
        break

    else:
        kalan_hak -= 1
        print("❌ Şifre yanlış.")

        if kalan_hak > 0:
            print("Kalan deneme hakkı:", kalan_hak)

        else:
            print("🚨 Kasa kilitlendi!")