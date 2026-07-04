"""
Kiro Registration Bot - Playwright Version with Async & Parallel Support
"""

import sys
import time
import json
import logging
import asyncio
from typing import Dict, List, Optional
from pathlib import Path

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError
import requests
from colorama import Fore, Style, init
from tqdm import tqdm

import config
from utils.helpers import setup_logging, save_tokens

# Initialize colorama
init(autoreset=True)

class KiroRegistrationBot:
    """Bot untuk registrasi Kiro menggunakan Google OAuth dengan Playwright"""

    def __init__(self, headless: bool = config.HEADLESS_MODE):
        self.headless = headless
        self.logger = logging.getLogger(__name__)
        self.accounts = []
        self.tokens = {}

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

    async def login_with_google(self, page: Page, email: str, password: str) -> Optional[str]:
        """Login ke Kiro menggunakan Google OAuth"""
        try:
            # Buka halaman login Kiro
            self.logger.info(f"{Fore.YELLOW}Membuka halaman login Kiro...{Style.RESET_ALL}")
            await page.goto(config.KIRO_LOGIN_URL, wait_until='domcontentloaded')
            await asyncio.sleep(2)

            # Screenshot untuk debugging
            screenshot_path = f"logs/screenshot_{email.replace('@', '_').replace('.', '_')}_{int(time.time())}.png"
            await page.screenshot(path=screenshot_path)
            self.logger.info(f"{Fore.CYAN}Screenshot disimpan: {screenshot_path}{Style.RESET_ALL}")

            # Handle cookie consent
            try:
                accept_btn = page.locator("button:has-text('Accept')")
                if await accept_btn.is_visible(timeout=3000):
                    await accept_btn.click()
                    self.logger.info(f"{Fore.GREEN}Cookie consent accepted{Style.RESET_ALL}")
                    await asyncio.sleep(1)
            except:
                self.logger.info(f"{Fore.CYAN}Tidak ada cookie consent dialog{Style.RESET_ALL}")

            # Klik tombol Google Sign in
            self.logger.info(f"{Fore.YELLOW}Mencari tombol login Google...{Style.RESET_ALL}")
            google_selectors = [
                "button:has-text('Google Sign in')",
                "button:has-text('Sign in with Google')",
                "button:has-text('Continue with Google')",
                "button:has-text('Google')",
            ]

            google_btn = None
            for selector in google_selectors:
                try:
                    btn = page.locator(selector).first
                    if await btn.is_visible(timeout=3000):
                        google_btn = btn
                        self.logger.info(f"{Fore.GREEN}Tombol Google ditemukan: {selector}{Style.RESET_ALL}")
                        break
                except:
                    continue

            if not google_btn:
                self.logger.error(f"{Fore.RED}Tidak ditemukan tombol Google{Style.RESET_ALL}")
                return None

            await google_btn.click()
            self.logger.info(f"{Fore.GREEN}Click berhasil{Style.RESET_ALL}")
            await asyncio.sleep(3)

            # Handle "Use another account" jika muncul
            try:
                use_another = page.locator("a:has-text('Use another account')")
                if await use_another.is_visible(timeout=3000):
                    self.logger.info(f"{Fore.YELLOW}Klik 'Use another account'...{Style.RESET_ALL}")
                    await use_another.click()
                    await asyncio.sleep(2)
            except:
                self.logger.info(f"{Fore.CYAN}Tidak ada halaman choose account{Style.RESET_ALL}")

            # Isi email
            self.logger.info(f"{Fore.YELLOW}Mengisi email...{Style.RESET_ALL}")
            email_input = page.locator("input[type='email'], input#identifierId").first
            await email_input.wait_for(state='visible', timeout=10000)
            await email_input.click()
            await email_input.fill(email)
            self.logger.info(f"{Fore.GREEN}Email diisi: {email[:3]}...{email[email.find('@'):]}{Style.RESET_ALL}")
            await asyncio.sleep(0.5)

            # Klik Next
            next_btn = page.locator("button:has-text('Next'), button#identifierNext").first
            await next_btn.click()
            await asyncio.sleep(3)

            # Isi password
            self.logger.info(f"{Fore.YELLOW}Mengisi password...{Style.RESET_ALL}")
            pwd_input = page.locator("input[type='password'], input[name='Passwd']").first
            await pwd_input.wait_for(state='visible', timeout=10000)
            await pwd_input.scroll_into_view_if_needed()
            await pwd_input.click()
            await asyncio.sleep(0.3)
            await pwd_input.fill(password)
            self.logger.info(f"{Fore.GREEN}Password diisi{Style.RESET_ALL}")
            await asyncio.sleep(1)

            # Klik Next untuk password - dengan wait dan multiple attempts
            self.logger.info(f"{Fore.YELLOW}Mencari tombol Next untuk password...{Style.RESET_ALL}")
            pwd_next_selectors = [
                "button:has-text('Next')",
                "button#passwordNext",
                "button[type='button']:has-text('Next')",
            ]

            pwd_next = None
            for selector in pwd_next_selectors:
                try:
                    btn = page.locator(selector).first
                    await btn.wait_for(state='visible', timeout=3000)
                    pwd_next = btn
                    self.logger.info(f"{Fore.GREEN}Next button found: {selector}{Style.RESET_ALL}")
                    break
                except:
                    continue

            if pwd_next:
                await pwd_next.click()
                self.logger.info(f"{Fore.GREEN}Password Next clicked{Style.RESET_ALL}")
                await asyncio.sleep(3)  # Wait longer for navigation
            else:
                # Fallback: press Enter
                self.logger.warning(f"{Fore.YELLOW}Next button not found, press Enter...{Style.RESET_ALL}")
                await pwd_input.press('Enter')
                await asyncio.sleep(3)

            # Handle consent pages (max 5 rounds)
            for consent_round in range(5):
                await asyncio.sleep(3)
                current_url = page.url
                self.logger.info(f"{Fore.CYAN}Consent round {consent_round+1}: {current_url[:80]}{Style.RESET_ALL}")

                # Jika sudah di Kiro, break
                if 'kiro' in current_url.lower() and 'google' not in current_url.lower():
                    self.logger.info(f"{Fore.GREEN}Sudah di Kiro, lanjut...{Style.RESET_ALL}")
                    break

                # Cari tombol consent
                clicked = False

                # Try "Continue" button
                try:
                    continue_btn = page.locator("button:has-text('Continue'), [jsname='uRHG6']").first
                    if await continue_btn.is_visible(timeout=3000):
                        await continue_btn.click()
                        self.logger.info(f"{Fore.GREEN}Klik 'Continue'{Style.RESET_ALL}")
                        clicked = True
                        continue
                except:
                    pass

                # Try "I understand" button (Workspace TOS)
                if not clicked:
                    try:
                        understand_btn = page.locator("button:has-text('I understand'), [jsname='Njthtb']").first
                        if await understand_btn.is_visible(timeout=3000):
                            await understand_btn.scroll_into_view_if_needed()
                            await understand_btn.click()
                            await asyncio.sleep(2)
                            # Check if URL changed
                            if 'speedbump' not in page.url and 'workspacetermsofservice' not in page.url:
                                self.logger.info(f"{Fore.GREEN}Klik 'I understand' berhasil{Style.RESET_ALL}")
                                clicked = True
                                continue
                    except:
                        pass

                # Try other consent buttons
                if not clicked:
                    for btn_text in ['I agree', 'Accept', 'Allow', 'Confirm']:
                        try:
                            btn = page.locator(f"button:has-text('{btn_text}')").first
                            if await btn.is_visible(timeout=2000):
                                await btn.click()
                                self.logger.info(f"{Fore.GREEN}Klik '{btn_text}'{Style.RESET_ALL}")
                                clicked = True
                                break
                        except:
                            continue

                if not clicked:
                    self.logger.info(f"{Fore.CYAN}Tidak ada tombol consent{Style.RESET_ALL}")
                    break

            # Jika masih di Google, navigate ke Kiro
            if 'google' in page.url.lower():
                self.logger.warning(f"{Fore.YELLOW}Masih di Google, navigate ke Kiro...{Style.RESET_ALL}")
                await page.goto(config.KIRO_BASE_URL, wait_until='domcontentloaded')
                await asyncio.sleep(5)

            # Tunggu redirect ke dashboard
            self.logger.info(f"{Fore.YELLOW}Menunggu redirect ke Kiro dashboard...{Style.RESET_ALL}")
            for wait_i in range(30):
                current_url = page.url
                if 'kiro' in current_url.lower() and '/signin' not in current_url.lower() and '/login' not in current_url.lower():
                    self.logger.info(f"{Fore.GREEN}Berada di Kiro dashboard: {current_url}{Style.RESET_ALL}")
                    break
                await asyncio.sleep(1)
            else:
                self.logger.warning(f"{Fore.YELLOW}Timeout redirect, URL: {page.url}{Style.RESET_ALL}")

            # Tunggu cookies di-set
            await asyncio.sleep(3)

            # Log cookies
            cookies = await page.context.cookies()
            self.logger.info(f"{Fore.CYAN}Cookies ({len(cookies)}){Style.RESET_ALL}")
            for c in cookies[:5]:
                self.logger.info(f"{Fore.CYAN}  '{c['name']}' = {c['value'][:60]}...{Style.RESET_ALL}")

            real_cookies = [c for c in cookies if c['name'] != 'kiro-visitor-id']
            if real_cookies:
                self.logger.info(f"{Fore.GREEN}Login berhasil untuk {email}{Style.RESET_ALL}")
            else:
                self.logger.warning(f"{Fore.YELLOW}Login mungkin GAGAL untuk {email}{Style.RESET_ALL}")

            return email

        except PlaywrightTimeoutError:
            self.logger.error(f"{Fore.RED}Timeout saat login untuk {email}{Style.RESET_ALL}")
            return None
        except Exception as e:
            self.logger.error(f"{Fore.RED}Error login untuk {email}: {str(e)}{Style.RESET_ALL}")
            return None

    async def extract_refresh_token(self, page: Page) -> Optional[str]:
        """Extract refresh token dari cookies"""
        try:
            current_url = page.url
            self.logger.info(f"{Fore.CYAN}Extract token dari URL: {current_url}{Style.RESET_ALL}")

            # Navigate ke Kiro base jika perlu
            needs_redirect = (
                'google' in current_url.lower() or
                'accounts.google' in current_url.lower() or
                '/signin' in current_url.lower() or
                '/login' in current_url.lower()
            )

            if needs_redirect:
                self.logger.warning(f"{Fore.YELLOW}URL bukan dashboard, navigating...{Style.RESET_ALL}")
                await page.goto(config.KIRO_BASE_URL, wait_until='domcontentloaded')
                await asyncio.sleep(5)

            # Get cookies
            cookies = await page.context.cookies()
            self.logger.info(f"{Fore.CYAN}Total cookies: {len(cookies)}{Style.RESET_ALL}")

            # Priority 1: RefreshToken
            for cookie in cookies:
                if cookie['name'] == 'RefreshToken':
                    token = cookie['value']
                    self.logger.info(f"{Fore.GREEN}✅ RefreshToken ditemukan!{Style.RESET_ALL}")
                    self.logger.info(f"{Fore.CYAN}Refresh Token: {token[:60]}...{Style.RESET_ALL}")
                    return token

            # Priority 2: auth_token
            for cookie in cookies:
                if cookie['name'] == 'auth_token':
                    self.logger.info(f"{Fore.GREEN}✅ auth_token ditemukan!{Style.RESET_ALL}")
                    return cookie['value']

            # Priority 3: any token
            for cookie in cookies:
                if ('refresh' in cookie['name'].lower() or 'token' in cookie['name'].lower()) and len(cookie['value']) > 20:
                    self.logger.info(f"{Fore.GREEN}✅ Token ditemukan: '{cookie['name']}'{Style.RESET_ALL}")
                    return cookie['value']

            self.logger.warning(f"{Fore.YELLOW}Tidak ditemukan token di {len(cookies)} cookies{Style.RESET_ALL}")
            return None

        except Exception as e:
            self.logger.error(f"{Fore.RED}Gagal mengekstrak token: {str(e)}{Style.RESET_ALL}")
            return None

    def send_to_9router(self, token: str, email: str) -> bool:
        """Kirim token ke 9router API"""
        try:
            payload = {"refreshToken": token}
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "KiroRegistrationBot/2.0",
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
                self.logger.info(f"{Fore.GREEN}Akun {email} berhasil dihapus{Style.RESET_ALL}")

        except Exception as e:
            self.logger.error(f"{Fore.RED}Gagal menghapus akun {email}: {str(e)}{Style.RESET_ALL}")

    async def process_account(self, browser: Browser, account: Dict, idx: int, total: int) -> bool:
        """Process single account"""
        email = account['email']
        password = account['password']

        self.logger.info(f"{Fore.CYAN}[{idx+1}/{total}] Memproses {email}{Style.RESET_ALL}")

        context = None
        try:
            # Create browser context
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            # Login
            result = await self.login_with_google(page, email, password)

            if result:
                # Extract token
                token = await self.extract_refresh_token(page)

                if token:
                    # Simpan token lokal
                    self.tokens[email] = token

                    # Kirim ke 9router
                    if self.send_to_9router(token, email):
                        self.logger.info(f"{Fore.GREEN}Akun {email} sukses diproses{Style.RESET_ALL}")
                        # Hapus akun yang berhasil
                        self.remove_account(email)
                        return True
                    else:
                        self.logger.warning(f"{Fore.YELLOW}Token {email} berhasil tapi gagal ke 9router{Style.RESET_ALL}")
                        return False
                else:
                    self.logger.error(f"{Fore.RED}Gagal mengekstrak token untuk {email}{Style.RESET_ALL}")
                    return False
            else:
                self.logger.error(f"{Fore.RED}Gagal login untuk {email}{Style.RESET_ALL}")
                return False

        except Exception as e:
            self.logger.error(f"{Fore.RED}Error processing {email}: {str(e)}{Style.RESET_ALL}")
            return False
        finally:
            if context:
                await context.close()
            await asyncio.sleep(1)

    async def process_accounts_parallel(self):
        """Process accounts dengan parallel execution"""
        self.accounts = self.load_accounts()

        if not self.accounts:
            self.logger.error(f"{Fore.RED}Tidak ada akun untuk diproses{Style.RESET_ALL}")
            return

        self.logger.info(f"{Fore.CYAN}Memulai proses {len(self.accounts)} akun (parallel: {config.PARALLEL_BROWSERS})...{Style.RESET_ALL}")

        success_count = 0
        failed_count = 0

        async with async_playwright() as p:
            # Pakai Chrome/Edge sistem (ga perlu download Chromium)
            try:
                browser = await p.chromium.launch(
                    channel='chrome',  # Pakai Chrome sistem
                    headless=self.headless,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-blink-features=AutomationControlled"
                    ]
                )
                self.logger.info(f"{Fore.GREEN}Menggunakan Chrome sistem{Style.RESET_ALL}")
            except Exception as e:
                # Fallback ke Edge (Windows 11 pasti punya)
                self.logger.info(f"{Fore.YELLOW}Chrome tidak ditemukan, pakai Edge...{Style.RESET_ALL}")
                browser = await p.chromium.launch(
                    channel='msedge',
                    headless=self.headless,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-blink-features=AutomationControlled"
                    ]
                )

            # Semaphore untuk limit concurrent browsers
            semaphore = asyncio.Semaphore(config.PARALLEL_BROWSERS)

            async def process_with_semaphore(account, idx):
                async with semaphore:
                    return await self.process_account(browser, account, idx, len(self.accounts))

            # Process dengan progress bar
            tasks = [process_with_semaphore(acc, i) for i, acc in enumerate(self.accounts)]

            # Run dengan tqdm
            results = []
            with tqdm(total=len(self.accounts), desc="Processing accounts") as pbar:
                for coro in asyncio.as_completed(tasks):
                    result = await coro
                    results.append(result)
                    pbar.update(1)

            await browser.close()

        # Count results
        success_count = sum(1 for r in results if r)
        failed_count = sum(1 for r in results if not r)

        # Simpan tokens
        save_tokens(self.tokens)

        # Print summary
        print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}SUKSES: {success_count} akun{Style.RESET_ALL}")
        print(f"{Fore.RED}GAGAL: {failed_count} akun{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Total diproses: {len(self.accounts)} akun{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

        # Hitung sisa akun
        remaining = self.load_accounts()
        print(f"{Fore.YELLOW}Sisa akun di {config.ACCOUNTS_FILE}: {len(remaining)} akun{Style.RESET_ALL}")

    def run(self):
        """Main execution"""
        try:
            setup_logging()
            asyncio.run(self.process_accounts_parallel())
        except KeyboardInterrupt:
            self.logger.info(f"{Fore.YELLOW}Bot dihentikan oleh user{Style.RESET_ALL}")
        except Exception as e:
            self.logger.error(f"{Fore.RED}Error fatal: {str(e)}{Style.RESET_ALL}")

def main():
    """Entry point"""
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Kiro Registration Bot v2.0 (Playwright + Async){Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

    headless = False
    if len(sys.argv) > 1:
        if '--headless' in sys.argv:
            headless = True
        if '--help' in sys.argv or '-h' in sys.argv:
            print(f"\n{Fore.YELLOW}Usage:{Style.RESET_ALL}")
            print("  python main.py [options]")
            print(f"\n{Fore.YELLOW}Options:{Style.RESET_ALL}")
            print("  --headless    Run in headless mode")
            print("  --help, -h    Show this help")
            return

    bot = KiroRegistrationBot(headless=headless)
    bot.run()

if __name__ == "__main__":
    main()
