#!/usr/bin/env python3
"""
Debug step by step untuk cari token Kiro
"""

print("=" * 60)
print("DEBUG KIRO TOKEN - STEP BY STEP")
print("=" * 60)

print("\nSTEP 1: Manual process untuk cari token:")
print("1. Buka browser manual (Chrome/Firefox)")
print("2. Buka URL: https://app.kiro.com/login")
print("3. Klik tombol 'Login with Google'")
print("4. Login dengan email/password Google")
print("5. Tunggu sampai masuk ke dashboard Kiro")
print("\nSTEP 2: Setelah login berhasil:")
print("1. Tekan F12 untuk buka DevTools")
print("2. Pilih tab 'Application' (atau 'Storage')")
print("3. Cari di:")
print("   a. Cookies → https://app.kiro.com")
print("   b. Local Storage → https://app.kiro.com")
print("   c. Session Storage → https://app.kiro.com")
print("\nSTEP 3: Cari token dengan nama:")
print("- auth_token")
print("- refresh_token")
print("- token")
print("- access_token")
print("- awsccc")
print("- kiro-session")
print("\nSTEP 4: Jika ditemukan, copy:")
print("1. Nama cookie/key")
print("2. Nilai token (yang panjang)")
print("\nSTEP 5: Share dengan saya untuk update script")
print("=" * 60)

print("\nQUICK FIX UNTUK SCRIPT:")
print("\n1. Tambahkan WAIT TIME lebih lama setelah login:")
print("   time.sleep(10)  # dari 5 ke 10 detik")

print("\n2. Cek localStorage juga:")
print("""
   # Di extract_refresh_token()
   try:
       localStorage = driver.execute_script("return JSON.stringify(localStorage)")
       if 'auth_token' in localStorage:
           print("Token ada di localStorage")
   except:
       pass
""")

print("\n3. Save page untuk inspection:")
print("""
   with open('debug_page.html', 'w', encoding='utf-8') as f:
       f.write(driver.page_source)
   print("Page saved untuk debugging")
""")

print("\n4. Check URL setelah login:")
print("""
   current_url = driver.current_url
   print(f"URL setelah login: {current_url}")
   if 'dashboard' in current_url or 'kiro.com' in current_url:
       print("Berhasil masuk ke Kiro")
   else:
       print("Belum masuk ke Kiro - mungkin masih di Google")
""")

print("=" * 60)
print("ACTION REQUIRED:")
print("1. Coba login MANUAL dulu untuk verify token location")
print("2. Share hasilnya untuk saya update script")
print("3. Atau, mau saya tambahkan wait time lebih lama di script?")
print("=" * 60)