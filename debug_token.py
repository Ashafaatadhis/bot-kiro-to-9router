#!/usr/bin/env python3
"""
Debug script untuk mencari refresh token di Kiro
"""

import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def debug_token_extraction(email, password):
    """Debug token extraction dengan manual inspection"""

    print(f"\n{'='*60}")
    print(f"DEBUG TOKEN EXTRACTION - {email}")
    print(f"{'='*60}")

    # Setup browser
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)

    try:
        # Step 1: Login ke Kiro
        print("\n[1] Buka Kiro login page...")
        driver.get("https://app.kiro.com/login")  # Update dengan URL benar
        time.sleep(3)

        # Save screenshot
        driver.save_screenshot(f"debug_login_{email.split('@')[0]}.png")
        print(f"   Screenshot saved: debug_login_{email.split('@')[0]}.png")

        # Step 2: Click Google button
        print("\n[2] Mencari tombol Google...")
        try:
            google_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Google')]"))
            )
            google_button.click()
            print("   Clicked Google button")
        except:
            print("   ERROR: Tombol Google tidak ditemukan")
            print("   Current URL:", driver.current_url)
            print("   Page source saved to: debug_page.html")
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            return

        time.sleep(3)

        # Step 3: Login Google
        print("\n[3] Login Google...")
        try:
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "identifierId"))
            )
            email_field.send_keys(email)
            print("   Email filled")

            next_button = driver.find_element(By.ID, "identifierNext")
            next_button.click()
            time.sleep(2)

            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "Passwd"))
            )
            password_field.send_keys(password)
            print("   Password filled")

            password_next = driver.find_element(By.ID, "passwordNext")
            password_next.click()
            print("   Submitted Google login")
        except Exception as e:
            print(f"   ERROR Google login: {e}")
            return

        # Wait for redirect to Kiro
        time.sleep(5)

        # Step 4: Extract semua storage
        print(f"\n[4] Extract semua storage - URL: {driver.current_url}")

        # 4a. Check localStorage
        print("\n   LOCAL STORAGE:")
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
                if value and len(value) > 10:  # Only show meaningful values
                    print(f"     {key}: {value[:100]}...")
                    if 'token' in key.lower() or 'refresh' in key.lower():
                        print(f"     ⭐ FOUND TOKEN in localStorage: {key}")
                        print(f"     Token value: {value[:50]}...")
        except Exception as e:
            print(f"     ERROR reading localStorage: {e}")

        # 4b. Check sessionStorage
        print("\n   SESSION STORAGE:")
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
                if value and len(value) > 10:
                    print(f"     {key}: {value[:100]}...")
                    if 'token' in key.lower() or 'refresh' in key.lower():
                        print(f"     ⭐ FOUND TOKEN in sessionStorage: {key}")
                        print(f"     Token value: {value[:50]}...")
        except Exception as e:
            print(f"     ERROR reading sessionStorage: {e}")

        # 4c. Check cookies
        print("\n   COOKIES:")
        cookies = driver.get_cookies()
        for cookie in cookies:
            print(f"     {cookie['name']}: {cookie['value'][:50]}...")
            if 'token' in cookie['name'].lower() or 'refresh' in cookie['name'].lower():
                print(f"     ⭐ FOUND TOKEN in cookies: {cookie['name']}")
                print(f"     Token value: {cookie['value'][:50]}...")

        # 4d. Check window object
        print("\n   WINDOW OBJECT KEYS (containing 'token' or 'refresh'):")
        try:
            window_keys = driver.execute_script("""
                var keys = [];
                for (var key in window) {
                    if (key.toLowerCase().includes('token') || key.toLowerCase().includes('refresh')) {
                        keys.push(key);
                    }
                }
                return keys;
            """)

            if window_keys:
                for key in window_keys:
                    try:
                        value = driver.execute_script(f"return window.{key}")
                        if value and isinstance(value, str) and len(value) > 10:
                            print(f"     window.{key}: {value[:100]}...")
                    except:
                        pass
        except Exception as e:
            print(f"     ERROR reading window object: {e}")

        # Step 5: Simulate storage access dari console
        print(f"\n[5] Manual JavaScript untuk akses storage:")
        js_scripts = [
            "return JSON.stringify(localStorage, null, 2)",
            "return JSON.stringify(sessionStorage, null, 2)",
            "return document.cookie",
            "return Object.keys(window).filter(k => k.toLowerCase().includes('token')).join(', ')",
            "return window.location.href"
        ]

        for i, js in enumerate(js_scripts, 1):
            try:
                result = driver.execute_script(js)
                if result and len(result) > 10:
                    print(f"\n   JS Script {i}:")
                    print(f"   {result[:200]}...")
            except Exception as e:
                print(f"   JS Script {i} error: {e}")

        # Step 6: Save final page untuk inspection
        driver.save_screenshot(f"debug_after_login_{email.split('@')[0]}.png")
        print(f"\n[6] Final screenshot saved: debug_after_login_{email.split('@')[0]}.png")

        print(f"\n{'='*60}")
        print("DEBUG COMPLETE")
        print(f"{'='*60}")

        # Suggest next steps
        print("\nNEXT STEPS:")
        print("1. Manually inspect browser: open DevTools (F12)")
        print("2. Check Application tab → Storage → Local Storage, Session Storage, Cookies")
        print("3. Look for keys containing: token, refresh, auth, jwt")
        print("4. Copy the key name and update extract_refresh_token() in main.py")

    finally:
        driver.quit()

def main():
    if len(sys.argv) < 3:
        print("Usage: python debug_token.py <email> <password>")
        print("Example: python debug_token.py kelxt1@lamakau.com Blokgamau123")
        return

    email = sys.argv[1]
    password = sys.argv[2]

    debug_token_extraction(email, password)

if __name__ == "__main__":
    main()