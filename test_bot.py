#!/usr/bin/env python3
"""
Test script for Kiro Registration Bot
"""

import os
import sys
import time
from pathlib import Path

def test_environment():
    """Test Python environment"""
    print("Testing Python environment...")

    # Check Python version
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")

    # Check required modules
    required_modules = [
        'selenium',
        'requests',
        'colorama',
        'tqdm',
        'beautifulsoup4',
        'webdriver_manager'
    ]

    print("\nChecking required modules...")
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"✗ {module} - not installed")
            return False

    return True

def test_files():
    """Test required files"""
    print("\nChecking required files...")

    required_files = [
        'account.txt',
        'config.py',
        'main.py'
    ]

    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - not found")
            all_exist = False

    return all_exist

def test_account_file():
    """Test account.txt format"""
    print("\nTesting account.txt format...")

    try:
        with open('account.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()

        valid_accounts = 0
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            if '|' in line:
                parts = line.split('|')
                if len(parts) == 2:
                    email, password = parts
                    if '@' in email and '.' in email and password:
                        valid_accounts += 1
                        print(f"✓ Line {i}: Valid format")
                    else:
                        print(f"✗ Line {i}: Invalid email/password")
                else:
                    print(f"✗ Line {i}: Should be email|password format")
            else:
                print(f"✗ Line {i}: Missing '|' separator")

        print(f"\nTotal valid accounts: {valid_accounts}")
        return valid_accounts > 0

    except Exception as e:
        print(f"✗ Error reading account.txt: {e}")
        return False

def test_config():
    """Test config.py"""
    print("\nTesting config.py...")

    try:
        # Import config
        import config

        # Check required variables
        required_vars = [
            'KIRO_BASE_URL',
            'KIRO_LOGIN_URL',
            'NINEROUTER_API',
            'BROWSER_TYPE',
            'WAIT_TIMEOUT',
            'ACCOUNTS_FILE',
            'TOKENS_FILE',
            'LOG_FILE'
        ]

        for var in required_vars:
            if hasattr(config, var):
                value = getattr(config, var)
                if value:
                    print(f"✓ {var} = {value}")
                else:
                    print(f"⚠ {var} is empty")
            else:
                print(f"✗ {var} not defined")

        return True

    except Exception as e:
        print(f"✗ Error importing config.py: {e}")
        return False

def quick_browser_test():
    """Quick browser test (non-headless)"""
    print("\nQuick browser test (will open browser briefly)...")

    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By

        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        print("Opening browser...")
        driver = webdriver.Chrome(options=options)

        # Open Google to test
        driver.get("https://www.google.com")
        time.sleep(2)

        # Get page title
        title = driver.title
        print(f"✓ Browser opened successfully")
        print(f"✓ Page title: {title}")

        # Close browser
        driver.quit()
        print("✓ Browser closed")

        return True

    except Exception as e:
        print(f"✗ Browser test failed: {e}")
        return False

def test_helper_functions():
    """Test helper functions"""
    print("\nTesting helper functions...")

    try:
        from utils import helpers

        # Test progress bar formatting
        progress = helpers.format_progress_bar(25, 100, 50)
        print(f"✓ Progress bar: {progress}")

        # Test account validation
        test_cases = [
            ("test@example.com", "password123", True),
            ("invalid-email", "pass", False),
            ("", "password", False),
            ("test@example.com", "", False),
        ]

        print("\nTesting account validation:")
        for email, password, expected in test_cases:
            result = helpers.validate_account_format(email, password)
            status = "✓" if result == expected else "✗"
            print(f"{status} {email}|{password} -> {result} (expected: {expected})")

        return True

    except Exception as e:
        print(f"✗ Helper functions test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("KIRO REGISTRATION BOT - TEST SUITE")
    print("=" * 60)

    tests = [
        ("Environment", test_environment),
        ("Files", test_files),
        ("Account File", test_account_file),
        ("Config", test_config),
        ("Helper Functions", test_helper_functions),
        ("Browser", quick_browser_test),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*40}")
        print(f"Test: {test_name}")
        print(f"{'='*40}")

        try:
            result = test_func()
            results.append((test_name, result))
            print(f"\nResult: {'PASS' if result else 'FAIL'}")
        except Exception as e:
            print(f"\n✗ Test crashed: {e}")
            results.append((test_name, False))

    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n✅ All tests passed! Bot is ready to run.")
        print("\nTo run the bot:")
        print("  python main.py")
        print("\nFor headless mode:")
        print("  python main.py --headless")
    else:
        print("\n⚠ Some tests failed. Please fix the issues above.")

    return passed == total

if __name__ == "__main__":
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    success = run_all_tests()
    sys.exit(0 if success else 1)