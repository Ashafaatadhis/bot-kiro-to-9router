"""
Kiro Registration Bot - Automate Google OAuth registration and token extraction
"""

import sys
import time
import json
import logging
import base64
from typing import Dict, List, Optional
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

import requests
from colorama import Fore, Style, init
from tqdm import tqdm

import config
from utils.helpers import setup_logging, extract_token_from_browser, save_tokens

# Initialize colorama
init(autoreset=True)

class KiroRegistrationBot:
    """Bot untuk registrasi Kiro menggunakan Google OAuth"""

    def __init__(self, headless: bool = config.HEADLESS_MODE):
        self.headless = headless
        self.driver = None
        self.logger = logging.getLogger(__name__)
        self.accounts = []
        self.tokens = {}

    def setup_driver(self):
        """Setup WebDriver berdasarkan konfigurasi"""
        try:
            if config.BROWSER_TYPE == "chrome":
                options = webdriver.ChromeOptions()
                if self.headless:
                    options.add_argument("--headless=new")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option("useAutomationExtension", False)

                # User agent untuk menghindari deteksi bot
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

                self.driver = webdriver.Chrome(
                    options=options
                )

            elif config.BROWSER_TYPE == "firefox":
                options = webdriver.FirefoxOptions()
                if self.headless:
                    options.add_argument("--headless")
                self.driver = webdriver.Firefox(options=options)

            elif config.BROWSER_TYPE == "edge":
                options = webdriver.EdgeOptions()
                if self.headless:
                    options.add_argument("--headless")
                self.driver = webdriver.Edge(options=options)

            else:
                raise ValueError(f"Browser type '{config.BROWSER_TYPE}' not supported")

            self.driver.maximize_window()
            self.logger.info(f"{Fore.GREEN}Browser berhasil diinisialisasi{Style.RESET_ALL}")
            return True

        except Exception as e:
            self.logger.error(f"{Fore.RED}Gagal menginisialisasi browser: {str(e)}{Style.RESET_ALL}")
            return False

    def load_accounts(self) -> List[Dict]:
        """Load akun dari file account.txt"""
        accounts = []
        try:
            with open(config.ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and '|' in line:
                        email, password = line.split('|', 1)
                        accounts.append({
                            'email': email.strip(),
                            'password': password.strip()
                        })

            self.logger.info(f"{Fore.GREEN}Berhasil memuat {len(accounts)} akun{Style.RESET_ALL}")
            return accounts

        except FileNotFoundError:
            self.logger.error(f"{Fore.RED}File {config.ACCOUNTS_FILE} tidak ditemukan{Style.RESET_ALL}")
            return []
        except Exception as e:
            self.logger.error(f"{Fore.RED}Gagal memuat akun: {str(e)}{Style.RESET_ALL}")
            return []

    def login_with_google(self, email: str, password: str) -> Optional[str]:
        """Login ke Kiro menggunakan Google OAuth"""
        try:
            # Buka halaman login Kiro
            self.logger.info(f"{Fore.YELLOW}Membuka halaman login Kiro...{Style.RESET_ALL}")
            self.driver.get(config.KIRO_LOGIN_URL)
            time.sleep(3)

            # SIMPAN WINDOW HANDLE KIRO (asli)
            kiro_window = self.driver.current_window_handle
            self.logger.info(f"{Fore.CYAN}Kiro window handle: {kiro_window}{Style.RESET_ALL}")

            # Ambil screenshot untuk debugging
            screenshot_path = f"logs/screenshot_{email.replace('@', '_').replace('.', '_')}_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_path)
            self.logger.info(f"{Fore.CYAN}Screenshot disimpan: {screenshot_path}{Style.RESET_ALL}")

            # Handle cookie consent dialog AWS (muncul duluan sebelum tombol Google)
            try:
                self.logger.info(f"{Fore.YELLOW}Mencari cookie consent dialog...{Style.RESET_ALL}")
                accept_cookies = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept')]"))
                )
                accept_cookies.click()
                self.logger.info(f"{Fore.GREEN}Cookie consent accepted{Style.RESET_ALL}")
                time.sleep(1)
            except:
                self.logger.info(f"{Fore.CYAN}Tidak ada cookie consent dialog{Style.RESET_ALL}")

            # Cari tombol login dengan Google
            self.logger.info(f"{Fore.YELLOW}Mencari tombol login Google...{Style.RESET_ALL}")

            # Selector berdasarkan Playwright snapshot: button "Google Sign in"
            google_selectors = [
                (By.XPATH, "//button[contains(., 'Google Sign in')]"),
                (By.XPATH, "//button[contains(., 'Sign in with Google')]"),
                (By.XPATH, "//button[contains(., 'Continue with Google')]"),
                (By.XPATH, "//button[contains(@aria-label, 'Google')]"),
                (By.XPATH, "//button[contains(., 'Google')]"),
                (By.CSS_SELECTOR, "button[class*='google']"),
            ]

            google_button = None
            for selector_type, selector_value in google_selectors:
                try:
                    self.logger.info(f"{Fore.CYAN}Mencoba selector: {selector_type}={selector_value}{Style.RESET_ALL}")
                    google_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    self.logger.info(f"{Fore.GREEN}Tombol Google ditemukan dengan selector: {selector_value}{Style.RESET_ALL}")
                    break
                except Exception as e:
                    continue

            if not google_button:
                self.logger.error(f"{Fore.RED}Tidak ditemukan tombol Google dengan selectors apapun{Style.RESET_ALL}")
                return None

            # Coba click dengan Selenium
            try:
                self.logger.info(f"{Fore.YELLOW}Mencoba klik tombol Google...{Style.RESET_ALL}")
                google_button.click()
                self.logger.info(f"{Fore.GREEN}Click berhasil{Style.RESET_ALL}")
            except Exception as click_error:
                self.logger.warning(f"{Fore.YELLOW}Selenium click gagal: {click_error}. Coba JavaScript click...{Style.RESET_ALL}")
                # Fallback ke JavaScript click
                self.driver.execute_script("arguments[0].click();", google_button)
                self.logger.info(f"{Fore.GREEN}JavaScript click berhasil{Style.RESET_ALL}")

            time.sleep(3)

            # Sekarang di halaman Google OAuth
            self.logger.info(f"{Fore.YELLOW}Di halaman Google OAuth...{Style.RESET_ALL}")
            time.sleep(2)

            # Check jika ada multiple tabs/windows
            if len(self.driver.window_handles) > 1:
                self.logger.info(f"{Fore.CYAN}Beralih ke window baru untuk Google OAuth...{Style.RESET_ALL}")
                self.driver.switch_to.window(self.driver.window_handles[-1])

            # Handle "choose account" page (jika ada multiple accounts)
            try:
                # Cek apakah ada "Use another account" link (element asli adalah <a>, bukan <div>)
                use_another = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Use another account')]"))
                )
                self.logger.info(f"{Fore.YELLOW}Halaman choose account terdeteksi, klik 'Use another account'...{Style.RESET_ALL}")
                use_another.click()
                time.sleep(2)
            except:
                self.logger.info(f"{Fore.CYAN}Tidak ada halaman choose account, langsung ke email input{Style.RESET_ALL}")

            # Tunggu sampai email field muncul
            self.logger.info(f"{Fore.YELLOW}Mencari email field Google...{Style.RESET_ALL}")

            # Selector alternatif untuk Google email field
            email_selectors = [
                (By.ID, "identifierId"),
                (By.NAME, "identifier"),
                (By.XPATH, "//input[@type='email']"),
                (By.CSS_SELECTOR, "input[type='email']"),
                (By.XPATH, "//input[contains(@aria-label, 'email')]"),
            ]

            email_field = None
            for selector_type, selector_value in email_selectors:
                try:
                    email_field = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    self.logger.info(f"{Fore.GREEN}Email field ditemukan: {selector_value}{Style.RESET_ALL}")
                    break
                except:
                    continue

            if not email_field:
                self.logger.error(f"{Fore.RED}Tidak ditemukan email field Google{Style.RESET_ALL}")
                return None

            # Clear field dulu, lalu isi email langsung tanpa delay
            email_field.clear()
            self.logger.info(f"{Fore.YELLOW}Mengisi email: {email[:3]}...{email[email.find('@'):]}{Style.RESET_ALL}")
            email_field.send_keys(email)  # Type langsung tanpa delay artificial

            time.sleep(0.5)  # Minimal wait

            # Cari tombol next - multiple selectors
            next_selectors = [
                (By.ID, "identifierNext"),
                (By.XPATH, "//button[contains(., 'Next')]"),
                (By.XPATH, "//button[contains(., 'Berikutnya')]"),
                (By.XPATH, "//div[contains(@role, 'button') and contains(., 'Next')]"),
                (By.CSS_SELECTOR, "button[jsname*='Next']"),
            ]

            next_button = None
            for selector_type, selector_value in next_selectors:
                try:
                    next_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    self.logger.info(f"{Fore.GREEN}Next button ditemukan: {selector_value}{Style.RESET_ALL}")
                    break
                except:
                    continue

            if next_button:
                next_button.click()
                time.sleep(3)
            else:
                self.logger.warning(f"{Fore.YELLOW}Tidak ditemukan next button, tekan Enter...{Style.RESET_ALL}")
                email_field.send_keys(Keys.RETURN)
                time.sleep(3)

            # Tunggu password field - multiple selectors
            self.logger.info(f"{Fore.YELLOW}Mencari password field...{Style.RESET_ALL}")
            password_selectors = [
                (By.NAME, "Passwd"),
                (By.NAME, "password"),
                (By.XPATH, "//input[@type='password']"),
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.XPATH, "//input[contains(@aria-label, 'password')]"),
            ]

            password_field = None
            for selector_type, selector_value in password_selectors:
                try:
                    password_field = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    self.logger.info(f"{Fore.GREEN}Password field ditemukan: {selector_value}{Style.RESET_ALL}")
                    break
                except:
                    continue

            if not password_field:
                self.logger.error(f"{Fore.RED}Tidak ditemukan password field{Style.RESET_ALL}")
                return None

            # Scroll ke element, click untuk focus, lalu isi password
            self.logger.info(f"{Fore.YELLOW}Mengisi password...{Style.RESET_ALL}")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", password_field)
            time.sleep(0.5)
            password_field.click()
            time.sleep(0.3)
            password_field.clear()
            password_field.send_keys(password)

            # Cari tombol next untuk password
            password_next = None
            for selector_type, selector_value in next_selectors:  # Reuse next_selectors
                try:
                    password_next = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    self.logger.info(f"{Fore.GREEN}Password next button ditemukan: {selector_value}{Style.RESET_ALL}")
                    break
                except:
                    continue

            if password_next:
                password_next.click()
            else:
                self.logger.warning(f"{Fore.YELLOW}Tidak ditemukan password next, tekan Enter...{Style.RESET_ALL}")
                password_field.send_keys(Keys.RETURN)

            self.logger.info(f"{Fore.GREEN}Google login submitted{Style.RESET_ALL}")

            # Handle semua halaman consent/TOS yang mungkin muncul (max 5 round)
            for consent_round in range(5):
                time.sleep(3)
                current_url = self.driver.current_url
                self.logger.info(f"{Fore.CYAN}Consent round {consent_round+1}: {current_url[:80]}{Style.RESET_ALL}")

                # Jika sudah di Kiro, break
                if 'kiro' in current_url.lower() and 'google' not in current_url.lower():
                    self.logger.info(f"{Fore.GREEN}Sudah di Kiro, lanjut...{Style.RESET_ALL}")
                    break

                # Cari tombol "Continue" / "I understand" / "Allow" / "Next"
                clicked = False

                # Priority 1: Cari tombol "Continue" (jsname="uRHG6") - OAuth consent
                for sel_type, sel_val in [
                    (By.CSS_SELECTOR, "[jsname='uRHG6'] button"),
                    (By.CSS_SELECTOR, "[jsname='uRHG6']"),
                    (By.XPATH, "//button[contains(., 'Continue')]"),
                    (By.XPATH, "//span[contains(., 'Continue')]/ancestor::button"),
                ]:
                    try:
                        btn = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((sel_type, sel_val))
                        )
                        if btn.is_displayed():
                            self.logger.info(f"{Fore.GREEN}Klik 'Continue' ({sel_val}){Style.RESET_ALL}")
                            btn.click()
                            clicked = True
                            break
                    except:
                        continue

                if clicked:
                    continue

                # Priority 2: Cari tombol "I understand" - Workspace TOS
                # Google Workspace TOS punya button spesifik dengan jsname='Njthtb'
                for sel_type, sel_val in [
                    (By.CSS_SELECTOR, "[jsname='Njthtb'] button"),
                    (By.CSS_SELECTOR, "[jsname='Njthtb']"),
                    (By.XPATH, "//button[contains(., 'I understand')]"),
                    (By.XPATH, "//span[contains(., 'I understand')]/ancestor::button"),
                ]:
                    try:
                        btn = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((sel_type, sel_val))
                        )
                        if btn.is_displayed():
                            self.logger.info(f"{Fore.GREEN}Klik 'I understand' ({sel_val}){Style.RESET_ALL}")
                            # Scroll ke element dulu
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                            time.sleep(0.5)
                            # JavaScript click langsung (lebih reliable untuk Google buttons)
                            self.driver.execute_script("arguments[0].click();", btn)
                            time.sleep(3)
                            # Cek apakah URL berubah
                            if 'speedbump' not in self.driver.current_url and 'workspacetermsofservice' not in self.driver.current_url:
                                clicked = True
                                self.logger.info(f"{Fore.GREEN}Berhasil klik 'I understand'{Style.RESET_ALL}")
                                break
                            else:
                                self.logger.warning(f"{Fore.YELLOW}Click '{sel_val}' gagal, coba selector berikutnya...{Style.RESET_ALL}")
                    except:
                        continue

                if clicked:
                    continue

                # Priority 2b: ActionChains fallback untuk "I understand"
                if not clicked and ('speedbump' in self.driver.current_url or 'workspacetermsofservice' in self.driver.current_url):
                    try:
                        self.logger.info(f"{Fore.YELLOW}Coba ActionChains click untuk I understand...{Style.RESET_ALL}")
                        btn = self.driver.find_element(By.CSS_SELECTOR, "[jsname='Njthtb']")
                        actions = ActionChains(self.driver)
                        actions.move_to_element(btn).click().perform()
                        time.sleep(3)
                        if 'speedbump' not in self.driver.current_url and 'workspacetermsofservice' not in self.driver.current_url:
                            clicked = True
                            self.logger.info(f"{Fore.GREEN}ActionChains berhasil!{Style.RESET_ALL}")
                    except Exception as e:
                        self.logger.warning(f"{Fore.YELLOW}ActionChains gagal: {e}{Style.RESET_ALL}")

                if clicked:
                    continue

                # Priority 3: Tombol consent lainnya
                for sel_type, sel_val in [
                    (By.XPATH, "//button[contains(., 'I agree')]"),
                    (By.XPATH, "//button[contains(., 'Accept')]"),
                    (By.XPATH, "//button[contains(., 'Allow')]"),
                    (By.XPATH, "//button[contains(., 'Confirm')]"),
                    (By.XPATH, "//button[contains(., 'Yes')]"),
                ]:
                    try:
                        btn = WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((sel_type, sel_val))
                        )
                        if btn.is_displayed():
                            self.logger.info(f"{Fore.GREEN}Klik '{btn.text}' ({sel_val}){Style.RESET_ALL}")
                            btn.click()
                            clicked = True
                            break
                    except:
                        continue

                if not clicked:
                    self.logger.info(f"{Fore.CYAN}Tidak ada tombol consent ditemukan, selesai{Style.RESET_ALL}")
                    break

            # Debug: cek URL saat ini (mungkin masih di Google)
            self.logger.info(f"{Fore.CYAN}URL setelah Google submit: {self.driver.current_url}{Style.RESET_ALL}")

            # Jika masih di Google setelah consent loop, coba navigate ke Kiro
            if 'google' in self.driver.current_url.lower():
                self.logger.warning(f"{Fore.YELLOW}Masih di Google setelah consent, coba navigate ke Kiro...{Style.RESET_ALL}")
                self.driver.get(config.KIRO_BASE_URL)
                time.sleep(5)
                self.logger.info(f"{Fore.CYAN}URL setelah navigate: {self.driver.current_url}{Style.RESET_ALL}")

            # SWITCH KEMBALI KE WINDOW KIRO (penting!)
            try:
                handles = self.driver.window_handles
                self.logger.info(f"{Fore.CYAN}Jumlah windows: {len(handles)}{Style.RESET_ALL}")

                # Log semua windows
                for i, handle in enumerate(handles):
                    self.driver.switch_to.window(handle)
                    self.logger.info(f"{Fore.CYAN}  Window {i}: {self.driver.current_url[:80]}{Style.RESET_ALL}")

                # Prioritas: switch ke window Kiro yang asli
                if kiro_window in handles:
                    self.driver.switch_to.window(kiro_window)
                    self.logger.info(f"{Fore.GREEN}Switch kembali ke window Kiro asli{Style.RESET_ALL}")
                else:
                    # Window Kiro mungkin sudah di-replace, cari window non-Google
                    for handle in handles:
                        self.driver.switch_to.window(handle)
                        url = self.driver.current_url
                        if 'google' not in url.lower():
                            self.logger.info(f"{Fore.GREEN}Switch ke window non-Google: {url[:80]}{Style.RESET_ALL}")
                            break
            except Exception as e:
                self.logger.warning(f"{Fore.YELLOW}Switch window error: {e}{Style.RESET_ALL}")

            # Tunggu sampai URL benar-benar di Kiro BUKAN di signin (max 30 detik)
            self.logger.info(f"{Fore.YELLOW}Menunggu redirect ke Kiro dashboard...{Style.RESET_ALL}")
            for wait_i in range(30):
                current_url = self.driver.current_url
                # Berhasil jika di Kiro dan BUKAN di halaman signin/login
                if 'kiro' in current_url.lower() and '/signin' not in current_url.lower() and '/login' not in current_url.lower():
                    self.logger.info(f"{Fore.GREEN}Berada di Kiro dashboard: {current_url}{Style.RESET_ALL}")
                    break
                self.logger.info(f"{Fore.CYAN}  [{wait_i+1}/30] URL: {current_url[:80]}{Style.RESET_ALL}")

                # Jika masih di Google setelah 10 detik, coba switch window lagi
                if wait_i == 10 and 'google' in current_url.lower():
                    self.logger.warning(f"{Fore.YELLOW}Masih di Google setelah 10 detik, coba switch window...{Style.RESET_ALL}")
                    for handle in self.driver.window_handles:
                        self.driver.switch_to.window(handle)
                        if 'google' not in self.driver.current_url.lower():
                            break

                time.sleep(1)
            else:
                self.logger.warning(f"{Fore.YELLOW}Timeout redirect, URL terakhir: {self.driver.current_url}{Style.RESET_ALL}")

            # Tunggu cookies di-set oleh Kiro
            time.sleep(3)

            # Log domain dan cookies
            final_url = self.driver.current_url
            self.logger.info(f"{Fore.CYAN}Domain final: {final_url}{Style.RESET_ALL}")
            cookies = self.driver.get_cookies()
            self.logger.info(f"{Fore.CYAN}Cookies ({len(cookies)}):{Style.RESET_ALL}")
            for c in cookies:
                self.logger.info(f"{Fore.CYAN}  '{c['name']}' = {c['value'][:60]}...{Style.RESET_ALL}")

            # Cek apakah benar-benar login (ada cookies selain kiro-visitor-id)
            real_cookies = [c for c in cookies if c['name'] != 'kiro-visitor-id']
            if real_cookies:
                self.logger.info(f"{Fore.GREEN}Login berhasil untuk {email} ({len(real_cookies)} cookies ditemukan){Style.RESET_ALL}")
            else:
                self.logger.warning(f"{Fore.YELLOW}Login mungkin GAGAL untuk {email} (hanya ada kiro-visitor-id){Style.RESET_ALL}")

            return email

        except TimeoutException:
            self.logger.error(f"{Fore.RED}Timeout saat login untuk {email}{Style.RESET_ALL}")
            return None
        except NoSuchElementException as e:
            self.logger.error(f"{Fore.RED}Element tidak ditemukan: {str(e)}{Style.RESET_ALL}")
            return None
        except Exception as e:
            self.logger.error(f"{Fore.RED}Error login untuk {email}: {str(e)}{Style.RESET_ALL}")
            return None

    def extract_refresh_token(self) -> Optional[str]:
        """Extract refresh token dari cookies Kiro"""
        try:
            # PENTING: Pastikan kita di domain Kiro yang benar (bukan signin, bukan Google)
            current_url = self.driver.current_url
            self.logger.info(f"{Fore.CYAN}Extract token dari URL: {current_url}{Style.RESET_ALL}")

            # Jika masih di Google domain atau signin page, navigate ke Kiro base
            needs_redirect = (
                'google' in current_url.lower() or
                'accounts.google' in current_url.lower() or
                '/signin' in current_url.lower() or
                '/login' in current_url.lower()
            )

            if needs_redirect:
                self.logger.warning(f"{Fore.YELLOW}URL bukan dashboard, navigating ke Kiro base...{Style.RESET_ALL}")
                self.driver.get(config.KIRO_BASE_URL)
                time.sleep(5)
                current_url = self.driver.current_url
                self.logger.info(f"{Fore.CYAN}URL setelah navigate: {current_url}{Style.RESET_ALL}")

            # Ambil SEMUA cookies (termasuk HttpOnly) via Selenium
            cookies = self.driver.get_cookies()
            self.logger.info(f"{Fore.CYAN}Total cookies di domain ini: {len(cookies)}{Style.RESET_ALL}")

            # Log semua cookies untuk debug
            for cookie in cookies:
                self.logger.info(f"{Fore.CYAN}  Cookie: '{cookie['name']}' = {cookie['value'][:60]}...{Style.RESET_ALL}")

            # PRIORITY 1: Cari cookie 'RefreshToken' (sesuai temuan user)
            for cookie in cookies:
                if cookie['name'] == 'RefreshToken':
                    token = cookie['value']
                    self.logger.info(f"{Fore.GREEN}✅ RefreshToken ditemukan!{Style.RESET_ALL}")
                    self.logger.info(f"{Fore.CYAN}Refresh Token: {token[:60]}...{Style.RESET_ALL}")
                    return token

            # PRIORITY 2: Cari cookie 'auth_token' (fallback)
            for cookie in cookies:
                if cookie['name'] == 'auth_token':
                    token = cookie['value']
                    self.logger.info(f"{Fore.GREEN}✅ auth_token ditemukan!{Style.RESET_ALL}")
                    return token

            # PRIORITY 3: Cari cookie dengan keyword 'refresh' (case-insensitive)
            for cookie in cookies:
                if 'refresh' in cookie['name'].lower() and len(cookie['value']) > 20:
                    token = cookie['value']
                    self.logger.info(f"{Fore.GREEN}✅ Token ditemukan: '{cookie['name']}'{Style.RESET_ALL}")
                    return token

            # PRIORITY 4: Cari cookie dengan keyword 'token' (case-insensitive)
            for cookie in cookies:
                if 'token' in cookie['name'].lower() and len(cookie['value']) > 20:
                    token = cookie['value']
                    self.logger.info(f"{Fore.GREEN}✅ Token ditemukan: '{cookie['name']}'{Style.RESET_ALL}")
                    return token

            # Tidak ditemukan - log debug info
            self.logger.warning(f"{Fore.YELLOW}Tidak ditemukan token di {len(cookies)} cookies{Style.RESET_ALL}")
            for cookie in cookies:
                self.logger.warning(f"  '{cookie['name']}' = {cookie['value'][:50]}...")

            return None

        except Exception as e:
            self.logger.error(f"{Fore.RED}Gagal mengekstrak token: {str(e)}{Style.RESET_ALL}")
            return None

    def send_to_9router(self, token: str, email: str) -> bool:
        """Kirim token ke 9router API"""
        try:
            # Format payload sesuai info dari user: {refreshToken: "token_value"}
            payload = {
                "refreshToken": token
            }

            headers = {
                "Content-Type": "application/json",
                "User-Agent": "KiroRegistrationBot/1.0",
                "Cookie": "_ga=GA1.1.1959781085.1782703277; auth_token=eyJhbGciOiJIUzI1NiJ9.eyJhdXRoZW50aWNhdGVkIjp0cnVlLCJpYXQiOjE3ODMwODk2NjQsImV4cCI6MTc4MzE3NjA2NH0._slQqwo4QIz9kW8UZofEJUXQ_6_1gI5xLGiPwb3RJJY; _ga_LC959F603F=GS2.1.s1783089661$o17$g1$t1783092588$j60$l0$h0"
            }

            response = requests.post(
                config.NINEROUTER_API,
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code in [200, 201]:
                self.logger.info(f"{Fore.GREEN}Token berhasil dikirim ke 9router{Style.RESET_ALL}")
                return True
            else:
                self.logger.error(f"{Fore.RED}Gagal mengirim token: {response.status_code} - {response.text}{Style.RESET_ALL}")
                return False

        except Exception as e:
            self.logger.error(f"{Fore.RED}Error mengirim ke 9router: {str(e)}{Style.RESET_ALL}")
            return False

    def remove_account(self, email: str):
        """Hapus akun yang sudah berhasil dari account.txt"""
        try:
            accounts_file = config.ACCOUNTS_FILE
            with open(accounts_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Filter baris yang bukan email yang berhasil
            new_lines = []
            removed = False
            for line in lines:
                stripped = line.strip()
                if stripped and '|' in stripped:
                    acc_email = stripped.split('|', 1)[0].strip()
                    if acc_email == email:
                        removed = True
                        self.logger.info(f"{Fore.GREEN}Menghapus {email} dari {accounts_file}{Style.RESET_ALL}")
                        continue
                new_lines.append(line)

            if removed:
                with open(accounts_file, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                self.logger.info(f"{Fore.GREEN}Akun {email} berhasil dihapus dari {accounts_file}{Style.RESET_ALL}")
            else:
                self.logger.warning(f"{Fore.YELLOW}Akun {email} tidak ditemukan di {accounts_file}{Style.RESET_ALL}")

        except Exception as e:
            self.logger.error(f"{Fore.RED}Gagal menghapus akun {email}: {str(e)}{Style.RESET_ALL}")

    def process_accounts(self):
        """Proses semua akun dengan browser fresh untuk setiap akun"""
        self.accounts = self.load_accounts()

        if not self.accounts:
            self.logger.error(f"{Fore.RED}Tidak ada akun untuk diproses{Style.RESET_ALL}")
            return

        self.logger.info(f"{Fore.CYAN}Memulai proses {len(self.accounts)} akun...{Style.RESET_ALL}")

        success_count = 0
        failed_count = 0

        for idx, account in enumerate(tqdm(self.accounts, desc="Processing accounts")):
            email = account['email']
            password = account['password']

            self.logger.info(f"{Fore.CYAN}[{idx+1}/{len(self.accounts)}] Memproses {email}{Style.RESET_ALL}")

            # Setup browser baru untuk setiap akun (fresh session)
            if self.driver:
                self.logger.info(f"{Fore.YELLOW}Menutup browser sebelumnya...{Style.RESET_ALL}")
                self.driver.quit()
                self.driver = None

            # Setup browser baru
            if not self.setup_driver():
                self.logger.error(f"{Fore.RED}Gagal setup browser untuk {email}{Style.RESET_ALL}")
                failed_count += 1
                continue

            try:
                # Login dengan Google
                result = self.login_with_google(email, password)

                if result:
                    # Extract token
                    token = self.extract_refresh_token()

                    if token:
                        # Simpan token lokal
                        self.tokens[email] = token

                        # Kirim ke 9router
                        if self.send_to_9router(token, email):
                            success_count += 1
                            self.logger.info(f"{Fore.GREEN}Akun {email} sukses diproses{Style.RESET_ALL}")
                            # Hapus akun yang berhasil dari account.txt
                            self.remove_account(email)
                        else:
                            failed_count += 1
                            self.logger.warning(f"{Fore.YELLOW}Token {email} berhasil tapi gagal ke 9router{Style.RESET_ALL}")
                    else:
                        failed_count += 1
                        self.logger.error(f"{Fore.RED}Gagal mengekstrak token untuk {email}{Style.RESET_ALL}")
                else:
                    failed_count += 1
                    self.logger.error(f"{Fore.RED}Gagal login untuk {email}{Style.RESET_ALL}")

            except Exception as e:
                self.logger.error(f"{Fore.RED}Error processing {email}: {str(e)}{Style.RESET_ALL}")
                failed_count += 1

            # Cleanup browser untuk akun ini
            if self.driver:
                self.logger.info(f"{Fore.YELLOW}Menutup browser untuk {email}...{Style.RESET_ALL}")
                self.driver.quit()
                self.driver = None

            # Short pause sebelum akun berikutnya (bisa dihapus untuk lebih cepat)
            if idx < len(self.accounts) - 1:
                time.sleep(2)  # Minimal pause

        # Simpan semua token ke file
        save_tokens(self.tokens)

        # Print summary
        print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}SUKSES: {success_count} akun{Style.RESET_ALL}")
        print(f"{Fore.RED}GAGAL: {failed_count} akun{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Total diproses: {len(self.accounts)} akun{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

        # Hitung sisa akun di account.txt
        remaining = self.load_accounts()
        print(f"{Fore.YELLOW}Sisa akun di {config.ACCOUNTS_FILE}: {len(remaining)} akun{Style.RESET_ALL}")

    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()
            self.logger.info(f"{Fore.GREEN}Browser ditutup{Style.RESET_ALL}")

    def run(self):
        """Main execution"""
        try:
            # Setup logging
            setup_logging()

            # Load accounts
            self.accounts = self.load_accounts()
            if not self.accounts:
                return

            # Setup driver
            if not self.setup_driver():
                return

            # Process accounts
            self.process_accounts()

        except KeyboardInterrupt:
            self.logger.info(f"{Fore.YELLOW}Bot dihentikan oleh user{Style.RESET_ALL}")
        except Exception as e:
            self.logger.error(f"{Fore.RED}Error fatal: {str(e)}{Style.RESET_ALL}")
        finally:
            self.cleanup()

def main():
    """Entry point"""
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Kiro Registration Bot v1.0{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

    # Parse arguments
    headless = False
    if len(sys.argv) > 1:
        if '--headless' in sys.argv:
            headless = True
        if '--help' in sys.argv or '-h' in sys.argv:
            print(f"\n{Fore.YELLOW}Usage:{Style.RESET_ALL}")
            print("  python main.py [options]")
            print(f"\n{Fore.YELLOW}Options:{Style.RESET_ALL}")
            print("  --headless    Run in headless mode (no browser visible)")
            print("  --help, -h    Show this help message")
            return

    # Run bot
    bot = KiroRegistrationBot(headless=headless)
    bot.run()

if __name__ == "__main__":
    main()