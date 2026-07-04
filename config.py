"""
Configuration file for Kiro registration bot
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Kiro URLs (contoh - perlu disesuaikan dengan URL sebenarnya)
KIRO_BASE_URL = "https://app.kiro.dev"
KIRO_LOGIN_URL = f"{KIRO_BASE_URL}/signin"
KIRO_GOOGLE_LOGIN_URL = f"{KIRO_BASE_URL}/auth/google"
KIRO_DASHBOARD_URL = f"{KIRO_BASE_URL}/dashboard"

# 9router endpoint (sesuai info dari user)
NINEROUTER_API = "http://localhost:20128/api/oauth/kiro/import"
NINEROUTER_METHOD = "POST"  # POST request

# Browser configuration
HEADLESS_MODE = False  # Set True untuk headless mode (tidak tampil browser)
BROWSER_TYPE = "chrome"  # chrome, firefox, edge
WAIT_TIMEOUT = 15  # Detik (dikurangi untuk lebih cepat)
TYPING_DELAY = 0  # 0 = tidak ada delay typing (kecepatan maksimal)
PARALLEL_BROWSERS = 2  # Jumlah browser yang jalan bersamaan (2-3 recommended)

# File paths
ACCOUNTS_FILE = "account.txt"
TOKENS_FILE = "tokens.json"
LOG_FILE = "logs/registration.log"

# Google OAuth config (contoh - perlu diisi dengan credentials sebenarnya)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8080/callback")