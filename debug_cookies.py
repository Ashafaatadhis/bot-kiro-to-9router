#!/usr/bin/env python3
"""
Debug script untuk melihat semua cookies yang benar-benar ada
"""

import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

def debug_all_cookies(email, password):
    """Debug semua cookies setelah login"""
    print(f"\n{'='*60}")
    print(f"DEBUG ALL COOKIES - {email}")
    print(f"{'='*60}")

    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    try:
        # 1. Login ke Kiro
        print("\n[1] Login ke Kiro...")
        driver.get("https://app.kiro.com/login")
        time.sleep(3)

        # Cari tombol Google
        google_button = None
        for xpath in [
            "//button[contains(., 'Google')]",
            "//a[contains(@href, 'google')]",
            "//div[contains(text(), 'Google')]"
        ]:
            try:
                google_button = driver.find_element(By.XPATH, xpath)
                print(f"   Tombol ditemukan: {xpath}")
                google_button.click()
                break
            except:
                continue

        if not google_button:
            print("   ❌ Tombol Google tidak ditemukan")
            return

        time.sleep(3)

        # 2. Login Google
        print("\n[2] Login Google...")
        try:
            # Email
            email_field = driver.find_element(By.ID, "identifierId")
            email_field.send_keys(email)
            print("   ✓ Email diisi")

            # Next button
            next_button = driver.find_element(By.ID, "identifierNext")
            next_button.click()
            time.sleep(2)

            # Password
            password_field = driver.find_element(By.NAME, "Passwd")
            password_field.send_keys(password)
            print("   ✓ Password diisi")

            # Submit
            password_next = driver.find_element(By.ID, "passwordNext")
            password_next.click()
            print("   ✓ Login Google submitted")

        except Exception as e:
            print(f"   ❌ Error login Google: {e}")
            return

        # 3. Tunggu dan cek cookies berulang
        print(f"\n[3] Checking cookies every 5 seconds...")

        for attempt in range(1, 7):  # 6 attempts = 30 seconds
            print(f"\n   Attempt {attempt}/6")
            time.sleep(5)

            # Get current URL
            current_url = driver.current_url
            print(f"   Current URL: {current_url}")

            # Get ALL cookies
            cookies = driver.get_cookies()
            print(f"   Total cookies: {len(cookies)}")

            # Print semua cookies dengan detail
            for i, cookie in enumerate(cookies, 1):
                print(f"\n     Cookie {i}:")
                print(f"       Name: '{cookie['name']}'")
                print(f"       Value: {cookie['value'][:100]}...")
                print(f"       Value length: {len(cookie['value'])}")
                print(f"       Domain: {cookie.get('domain', 'N/A')}")
                print(f"       Path: {cookie.get('path', 'N/A')}")

                # Highlight important cookies
                if cookie['name'] == 'RefreshToken':
                    print(f"       ⭐⭐⭐ FOUND RefreshToken!")
                elif cookie['name'] == 'auth_token':
                    print(f"       ⭐⭐ FOUND auth_token!")
                elif 'token' in cookie['name'].lower():
                    print(f"       ⭐ Token-like cookie detected")
                elif 'refresh' in cookie['name'].lower():
                    print(f"       ⭐ Refresh-like cookie detected")

            # Check if we have RefreshToken
            for cookie in cookies:
                if cookie['name'] == 'RefreshToken':
                    print(f"\n   ✅ RefreshToken ditemukan pada attempt {attempt}!")
                    print(f"   Token value: {cookie['value'][:100]}...")
                    return cookie['value']

        print(f"\n❌ RefreshToken tidak ditemukan setelah 30 detik")

        # Final check
        print(f"\n[4] Final analysis:")
        cookies = driver.get_cookies()
        print(f"   Final total cookies: {len(cookies)}")

        for cookie in cookies:
            print(f"   - '{cookie['name']}' = {cookie['value'][:30]}...")

        print(f"\n[5] Recommendations:")
        if len(cookies) == 0:
            print("   ❌ Tidak ada cookies sama sekali - login mungkin gagal")
        elif any('kiro' in c['name'].lower() for c in cookies):
            print("   ✓ Ada cookies Kiro, tapi tidak ada RefreshToken")
            print("   ⚠️ Mungkin perlu waktu lebih lama atau interaksi manual")
        else:
            print("   ❌ Tidak ada cookies Kiro - mungkin masih di Google login")

        # Save screenshot
        driver.save_screenshot("debug_cookies_final.png")
        print(f"   Screenshot saved: debug_cookies_final.png")

        return None

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        print(f"\n[6] Browser akan ditutup dalam 10 detik...")
        time.sleep(10)
        driver.quit()

def main():
    if len(sys.argv) < 3:
        print("Usage: python debug_cookies.py <email> <password>")
        print("Example: python debug_cookies.py kelxt1@lamakau.com Blokgamau123")
        return

    email = sys.argv[1]
    password = sys.argv[2]

    token = debug_all_cookies(email, password)

    if token:
        print(f"\n{'='*60}")
        print(f"✅ SUCCESS: RefreshToken ditemukan!")
        print(f"{'='*60}")
        print(f"\nToken: {token[:100]}...")
        print(f"Token length: {len(token)}")
    else:
        print(f"\n{'='*60}")
        print(f"❌ FAILED: RefreshToken tidak ditemukan")
        print(f"{'='*60}")

if __name__ == "__main__":
    main()