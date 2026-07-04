"""
Helper functions for Kiro Registration Bot
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

import config

def setup_logging():
    """Setup logging configuration"""
    log_dir = Path(config.LOG_FILE).parent
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def extract_token_from_browser(driver) -> str:
    """
    Extract authentication token from browser
    Tries multiple methods:
    1. Local storage
    2. Cookies
    3. Session storage
    """
    token = None

    # Method 1: Local storage
    try:
        token = driver.execute_script("""
            return localStorage.getItem('refresh_token') ||
                   localStorage.getItem('access_token') ||
                   localStorage.getItem('auth_token') ||
                   localStorage.getItem('token');
        """)
    except:
        pass

    # Method 2: Cookies
    if not token:
        try:
            cookies = driver.get_cookies()
            for cookie in cookies:
                if any(keyword in cookie['name'].lower() for keyword in ['refresh', 'token', 'auth']):
                    token = cookie['value']
                    break
        except:
            pass

    # Method 3: Session storage
    if not token:
        try:
            token = driver.execute_script("""
                return sessionStorage.getItem('refresh_token') ||
                       sessionStorage.getItem('access_token') ||
                       sessionStorage.getItem('auth_token') ||
                       sessionStorage.getItem('token');
            """)
        except:
            pass

    return token

def save_tokens(tokens: Dict[str, str]):
    """Save tokens to JSON file"""
    try:
        # Add metadata
        token_data = {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "total_tokens": len(tokens),
                "source": "kiro_registration_bot"
            },
            "tokens": tokens
        }

        with open(config.TOKENS_FILE, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, indent=2, ensure_ascii=False)

        logging.info(f"Tokens saved to {config.TOKENS_FILE}")
        return True

    except Exception as e:
        logging.error(f"Failed to save tokens: {str(e)}")
        return False

def load_tokens() -> Dict[str, str]:
    """Load tokens from JSON file"""
    try:
        if Path(config.TOKENS_FILE).exists():
            with open(config.TOKENS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("tokens", {})
        return {}
    except Exception as e:
        logging.error(f"Failed to load tokens: {str(e)}")
        return {}

def validate_account_format(email: str, password: str) -> bool:
    """Validate email and password format"""
    if not email or not password:
        return False

    # Basic email validation
    if '@' not in email or '.' not in email:
        return False

    # Password length check
    if len(password) < 6:
        return False

    return True

def format_progress_bar(current: int, total: int, length: int = 50) -> str:
    """Create a text-based progress bar"""
    percent = current / total
    filled_length = int(length * percent)
    bar = '█' * filled_length + '░' * (length - filled_length)
    return f"[{bar}] {current}/{total} ({percent:.1%})"

def sleep_with_progress(seconds: int, message: str = "Waiting"):
    """Sleep with progress indicator"""
    print(f"\n{message} for {seconds} seconds...")
    for i in range(seconds):
        time.sleep(1)
        progress = format_progress_bar(i + 1, seconds, 30)
        print(f"\r{progress}", end='', flush=True)
    print()

def sanitize_log_data(data: Any) -> Any:
    """Sanitize sensitive data for logging"""
    if isinstance(data, str):
        # Mask email addresses
        if '@' in data:
            parts = data.split('@')
            if len(parts[0]) > 2:
                masked = parts[0][:2] + '*' * (len(parts[0]) - 2)
                return f"{masked}@{parts[1]}"

        # Mask passwords
        if '|' in data:
            email, password = data.split('|', 1)
            if len(password) > 2:
                masked_pw = password[:2] + '*' * (len(password) - 2)
                return f"{email}|{masked_pw}"

    elif isinstance(data, dict):
        return {k: sanitize_log_data(v) for k, v in data.items()}

    return data

def check_requirements():
    """Check if required files exist"""
    required_files = [config.ACCOUNTS_FILE]

    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)

    if missing:
        print(f"Error: Missing required files: {', '.join(missing)}")
        print(f"Please create {config.ACCOUNTS_FILE} with email|password format")
        return False

    return True