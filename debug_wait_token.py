#!/usr/bin/env python3
"""
Debug script untuk wait token muncul
"""

import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def debug_wait_token(email, password):
    """Wait untuk token muncul"""

    print(f"\n{'='*60}")
    print(f"DEBUG WAIT TOKEN - {email}")
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
        print("   ✓ Google login submitted")

        # 2. Wait untuk redirect dan token muncul
        print("\n[2] Waiting for token to appear...")

        for i in range(1, 31):  # Wait up to 30 seconds
            print(f"   {i}/30 seconds...")

            # Check URL
            current_url = driver.current_url
            print(f"   URL: {current_url}")

            # Check cookies
            cookies = driver.get_cookies()
            print(f"   Cookies: {len(cookies)}")

            for cookie in cookies:
                print(f"     {cookie['name']}: {cookie['value'][:50]}...")
                if cookie['name'] == 'auth_token':
                    print(f"   ⭐ FOUND auth_token!")
                    print(f"   Token: {cookie['value'][:100]}...")
                    return cookie['value']

            # Check localStorage
            try:
                localStorage = driver.execute_script("""
                    var items = {};
                    for (var i = 0; i < localStorage.length; i++) {
                        var key = localStorage.key(i);
                        items[key] = localStorage.getItem(key);
                    }
                    return JSON.stringify(items, null, 2);
                """)

                if localStorage and len(localStorage) > 10:
                    print(f"   LocalStorage keys: {localStorage[:200]}...")

                    # Check for token in localStorage
                    localStorage_dict = driver.execute_script("""
                        var items = {};
                        for (var i = 0; i < localStorage.length; i++) {
                            var key = localStorage.key(i);
                            items[key] = localStorage.getItem(key);
                        }
                        return items;
                    """)

                    for key, value in localStorage_dict.items():
                        if 'token' in key.lower() or 'auth' in key.lower():
                            print(f"   ⭐ FOUND token in localStorage: {key}")
                            print(f"   Value: {value[:100]}...")
                            return value
            except Exception as e:
                print(f"   LocalStorage error: {e}")

            time.sleep(1)

        print("\n❌ Token not found after 30 seconds")

        # Save page for debugging
        print("\n[3] Saving page for debugging...")
        with open("debug_page_no_token.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("   Page saved: debug_page_no_token.html")

        driver.save_screenshot("debug_no_token.png")
        print("   Screenshot saved: debug_no_token.png")

        return None

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return None

    finally:
        driver.quit()

def main():
    if len(sys.argv) < 3:
        print("Usage: python debug_wait_token.py <email> <password>")
        print("Example: python debug_wait_token.py kelxt1@lamakau.com Blokgamau123")
        return

    email = sys.argv[1]
    password = sys.argv[2]

    token = debug_wait_token(email, password)

    if token:
        print(f"\n{'='*60}")
        print("✅ TOKEN FOUND!")
        print(f"{'='*60}")
        print(f"\nToken: {token[:100]}...")
        print(f"Token length: {len(token)}")

        # Test send to 9router
        print(f"\n[4] Testing 9router API...")
        import requests
        import json

        payload = {"refreshToken": token}

        try:
            response = requests.post(
                "http://localhost:20128/api/oauth/kiro/import",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   Error: {e}")
    else:
        print(f"\n{'='*60}")
        print("❌ NO TOKEN FOUND")
        print(f"{'='=60}")

if __name__ == "__main__":
    main()