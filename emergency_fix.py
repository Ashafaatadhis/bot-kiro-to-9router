#!/usr/bin/env python3
"""
Emergency fix untuk extract token dari cookie awsccc
"""

import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def emergency_token_fix(email, password):
    """Force extract token dari cookie awsccc"""
    print(f"\n{'='*60}")
    print(f"EMERGENCY TOKEN FIX - {email}")
    print(f"{'='*60}")

    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        # 1. Login ke Kiro
        print("\n[1] Login ke Kiro...")
        driver.get("https://app.kiro.com/login")
        time.sleep(3)

        # Click Google button
        google_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Google')]"))
        )
        google_button.click()
        time.sleep(3)

        # Login Google
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "identifierId"))
        )
        email_field.send_keys(email)

        next_button = driver.find_element(By.ID, "identifierNext")
        next_button.click()
        time.sleep(2)

        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "Passwd"))
        )
        password_field.send_keys(password)

        password_next = driver.find_element(By.ID, "passwordNext")
        password_next.click()
        time.sleep(5)

        print("   ✓ Login berhasil")

        # 2. Extract cookies
        print("\n[2] Extract semua cookies...")
        cookies = driver.get_cookies()
        print(f"   Total cookies: {len(cookies)}")

        # Cari cookie awsccc
        awsccc_token = None
        for cookie in cookies:
            print(f"   {cookie['name']}: {cookie['value'][:50]}...")
            if cookie['name'] == 'awsccc':
                awsccc_token = cookie['value']
                print(f"   ⭐ FOUND awsccc token!")

        # 3. Kirim ke 9router
        if awsccc_token:
            print(f"\n[3] Kirim ke 9router...")

            import requests
            import json

            payload = {
                "refreshToken": awsccc_token
            }

            headers = {
                "Content-Type": "application/json"
            }

            try:
                response = requests.post(
                    "http://localhost:20128/api/oauth/kiro/import",
                    json=payload,
                    headers=headers,
                    timeout=30
                )

                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")

                if response.status_code in [200, 201]:
                    print("   ✅ Token berhasil dikirim ke 9router!")
                else:
                    print("   ❌ Gagal mengirim token")

            except Exception as e:
                print(f"   ❌ Error: {e}")

            # 4. Simpan token
            print(f"\n[4] Simpan token...")
            token_data = {
                "email": email,
                "token": awsccc_token[:50] + "...",
                "timestamp": int(time.time())
            }

            with open("emergency_token.json", "w", encoding="utf-8") as f:
                json.dump(token_data, f, indent=2)

            print(f"   ✅ Token disimpan ke emergency_token.json")

        else:
            print("   ❌ Cookie awsccc tidak ditemukan")

        print(f"\n{'='*60}")
        print("EMERGENCY FIX COMPLETE")
        print(f"{'='*60}")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")

    finally:
        driver.quit()

def main():
    if len(sys.argv) < 3:
        print("Usage: python emergency_fix.py <email> <password>")
        print("Example: python emergency_fix.py kelxt1@lamakau.com Blokgamau123")
        return

    email = sys.argv[1]
    password = sys.argv[2]

    emergency_token_fix(email, password)

if __name__ == "__main__":
    main()