#!/usr/bin/env python3
"""
Simple debug untuk cari token Kiro
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# Setup browser
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=options)

try:
    # 1. Buka Kiro
    print("1. Buka https://app.kiro.com/login")
    driver.get("https://app.kiro.com/login")
    time.sleep(3)
    print(f"   URL: {driver.current_url}")

    # 2. Cari tombol Google
    print("\n2. Cari tombol Google...")
    google_buttons = driver.find_elements(By.XPATH, "//button | //a | //div")

    for btn in google_buttons[:10]:
        text = btn.text.lower()
        if "google" in text:
            print(f"   Found button: {btn.text[:50]}")
            btn.click()
            print("   Clicked!")
            break

    time.sleep(3)

    # 3. Login Google
    print("\n3. Login Google...")
    print("   Please login manually, then press Enter in this terminal")
    input("   Press Enter after manual login...")

    # 4. Check cookies setiap 5 detik
    print("\n4. Checking cookies every 5 seconds...")
    for i in range(10):
        print(f"\n   Check {i+1}/10 - Wait 5 seconds...")
        time.sleep(5)

        cookies = driver.get_cookies()
        print(f"   Total cookies: {len(cookies)}")

        for cookie in cookies:
            print(f"     {cookie['name']}: {cookie['value'][:50]}...")
            if cookie['name'] == 'auth_token':
                print(f"\n⭐ FOUND auth_token!")
                print(f"Token: {cookie['value']}")
                break

        # Check URL juga
        print(f"   Current URL: {driver.current_url}")

    print("\n5. Final check...")
    driver.save_screenshot("final_debug.png")
    print("   Screenshot saved: final_debug.png")

finally:
    print("\nBrowser akan tetap terbuka untuk manual inspection...")
    print("Check DevTools (F12) → Application tab → Storage")
    print("1. Cookies")
    print("2. Local Storage")
    print("3. Session Storage")
    input("\nPress Enter to close browser...")
    driver.quit()