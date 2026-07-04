#!/usr/bin/env python3
"""
EMERGENCY FIX: Cari token di semua tempat setelah login
"""

import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def find_token_anywhere(email, password):
    """Cari token di SEMUA tempat yang mungkin"""

    print(f"\n{'='*60}")
    print(f"EMERGENCY TOKEN SEARCH - {email}")
    print(f"{'='*60}")

    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        # STEP 1: Login ke Kiro
        print("\n[1] Login ke Kiro...")
        driver.get("https://app.kiro.dev/signin")
        time.sleep(3)

        # Cari dan klik tombol Google
        print("   Mencari tombol Google...")
        google_button = None
        for xpath in [
            "//button[contains(., 'Google')]",
            "//button[contains(@aria-label, 'Google')]",
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
            return None

        time.sleep(3)

        # STEP 2: Login Google
        print("\n[2] Login Google...")
        try:
            # Email
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "identifierId"))
            )
            email_field.send_keys(email)
            print("   ✓ Email diisi")

            # Next button
            next_button = driver.find_element(By.ID, "identifierNext")
            next_button.click()
            time.sleep(2)

            # Password
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "Passwd"))
            )
            password_field.send_keys(password)
            print("   ✓ Password diisi")

            # Submit
            password_next = driver.find_element(By.ID, "passwordNext")
            password_next.click()
            print("   ✓ Login Google submitted")

        except Exception as e:
            print(f"   ❌ Error login Google: {e}")
            return None

        # STEP 3: WAIT LAMA untuk token muncul
        print(f"\n[3] Waiting 15 seconds for token...")
        for i in range(1, 16):
            print(f"   {i}/15 seconds...")
            time.sleep(1)

        # STEP 4: Cari token di SEMUA tempat
        print(f"\n[4] Searching token in ALL locations...")

        found_token = None

        # 4a. Check COOKIES
        print(f"\n   COOKIES:")
        cookies = driver.get_cookies()
        print(f"   Total cookies: {len(cookies)}")

        for cookie in cookies:
            print(f"     {cookie['name']}: {cookie['value'][:50]}...")
            if cookie['name'] == 'auth_token':
                found_token = cookie['value']
                print(f"     ⭐ FOUND auth_token in cookies!")

        # 4b. Check LOCALSTORAGE
        print(f"\n   LOCAL STORAGE:")
        try:
            localStorage = driver.execute_script("""
                var items = {};
                for (var i = 0; i < localStorage.length; i++) {
                    var key = localStorage.key(i);
                    items[key] = localStorage.getItem(key);
                }
                return items;
            """)

            for key, value in localStorage.items():
                if value and len(value) > 20:
                    print(f"     {key}: {value[:50]}...")
                    if 'token' in key.lower() or 'auth' in key.lower():
                        found_token = value
                        print(f"     ⭐ FOUND token in localStorage: {key}")

        except Exception as e:
            print(f"     Error: {e}")

        # 4c. Check SESSIONSTORAGE
        print(f"\n   SESSION STORAGE:")
        try:
            sessionStorage = driver.execute_script("""
                var items = {};
                for (var i = 0; i < sessionStorage.length; i++) {
                    var key = sessionStorage.key(i);
                    items[key] = sessionStorage.getItem(key);
                }
                return items;
            """)

            for key, value in sessionStorage.items():
                if value and len(value) > 20:
                    print(f"     {key}: {value[:50]}...")
                    if 'token' in key.lower() or 'auth' in key.lower():
                        found_token = value
                        print(f"     ⭐ FOUND token in sessionStorage: {key}")

        except Exception as e:
            print(f"     Error: {e}")

        # 4d. Check URL dan page
        print(f"\n   PAGE INFO:")
        print(f"     URL: {driver.current_url}")
        print(f"     Title: {driver.title}")

        # Save screenshot dan page source
        driver.save_screenshot("emergency_debug.png")
        print(f"     Screenshot saved: emergency_debug.png")

        with open("emergency_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source[:50000])  # First 50k chars
        print(f"     Page saved: emergency_page.html")

        # STEP 5: Return token jika ditemukan
        if found_token:
            print(f"\n{'='*60}")
            print(f"✅ TOKEN FOUND!")
            print(f"{'='*60}")
            print(f"\nToken: {found_token[:100]}...")
            print(f"Token length: {len(found_token)}")

            # Coba kirim ke 9router
            print(f"\n[5] Testing 9router API...")
            import requests
            import json

            payload = {"refreshToken": found_token}

            try:
                response = requests.post(
                    "http://localhost:20128/api/oauth/kiro/import",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )

                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")

                if response.status_code in [200, 201]:
                    print("   ✅ Token berhasil dikirim ke 9router!")
                else:
                    print("   ❌ Gagal mengirim token")

            except Exception as e:
                print(f"   Error: {e}")

            return found_token
        else:
            print(f"\n{'='*60}")
            print(f"❌ NO TOKEN FOUND ANYWHERE")
            print(f"{'='*60}")

            print(f"\nNEXT STEPS:")
            print("1. Check screenshot: emergency_debug.png")
            print("2. Check page source: emergency_page.html")
            print("3. Manual inspect dengan F12 → Application tab")
            print("4. Cari di: Cookies, Local Storage, Session Storage")

            return None

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return None

    finally:
        # Biarkan browser tetap terbuka untuk debugging
        print(f"\nBrowser tetap terbuka untuk debugging...")
        print("Tekan Enter untuk menutup browser...")
        input()
        driver.quit()

def main():
    if len(sys.argv) < 3:
        print("Usage: python emergency_token_fix.py <email> <password>")
        print("Example: python emergency_token_fix.py kelxt1@lamakau.com Blokgamau123")
        return

    email = sys.argv[1]
    password = sys.argv[2]

    find_token_anywhere(email, password)

if __name__ == "__main__":
    main()