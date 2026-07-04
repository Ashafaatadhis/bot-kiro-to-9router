#!/usr/bin/env python3
"""
Setup script for Kiro Registration Bot
"""

import os
import sys
import shutil
from pathlib import Path

def print_header():
    """Print installation header"""
    print("=" * 60)
    print("KIRO REGISTRATION BOT - SETUP")
    print("=" * 60)

def check_python_version():
    """Check Python version"""
    print("\n[1/6] Checking Python version...")
    if sys.version_info < (3, 7):
        print("✗ Python 3.7 or higher required")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected")
    return True

def create_virtual_env():
    """Create virtual environment"""
    print("\n[2/6] Setting up virtual environment...")

    venv_dir = "venv"
    if Path(venv_dir).exists():
        print(f"✓ Virtual environment '{venv_dir}' already exists")
        return True

    try:
        import venv
        venv.create(venv_dir, with_pip=True)
        print(f"✓ Virtual environment created: {venv_dir}")
        return True
    except Exception as e:
        print(f"✗ Failed to create virtual environment: {e}")
        print("You can create it manually: python -m venv venv")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("\n[3/6] Installing dependencies...")

    if not Path("requirements.txt").exists():
        print("✗ requirements.txt not found")
        return False

    # Determine pip command based on platform
    if os.name == "nt":  # Windows
        pip_cmd = os.path.join("venv", "Scripts", "pip")
    else:  # Unix/Linux/Mac
        pip_cmd = os.path.join("venv", "bin", "pip")

    try:
        # Upgrade pip first
        os.system(f"{pip_cmd} install --upgrade pip")

        # Install requirements
        result = os.system(f"{pip_cmd} install -r requirements.txt")
        if result == 0:
            print("✓ Dependencies installed successfully")
            return True
        else:
            print("✗ Failed to install dependencies")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def setup_files():
    """Setup configuration files"""
    print("\n[4/6] Setting up configuration files...")

    # Check if account.txt exists
    if not Path("account.txt").exists():
        print("⚠ account.txt not found - creating example file")
        example_accounts = """kelxt1@lamakau.com|Blokgamau123
kelxt2@lamakau.com|Blokgamau123
kelxt3@lamakau.com|Blokgamau123"""

        with open("account.txt", "w", encoding="utf-8") as f:
            f.write(example_accounts)
        print("✓ Created example account.txt")
    else:
        print("✓ account.txt already exists")

    # Check if .env exists
    if not Path(".env").exists():
        if Path(".env.example").exists():
            shutil.copy(".env.example", ".env")
            print("✓ Created .env from .env.example")
            print("⚠ Please edit .env file with your credentials")
        else:
            print("✗ .env.example not found")
    else:
        print("✓ .env already exists")

    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    print("✓ Created logs directory")

    return True

def check_browser():
    """Check if browser is available"""
    print("\n[5/6] Checking browser availability...")

    browsers = ["chrome", "firefox", "edge"]
    available = []

    import webbrowser
    for browser in browsers:
        try:
            webbrowser.get(browser)
            available.append(browser)
        except:
            pass

    if available:
        print(f"✓ Available browsers: {', '.join(available)}")
        print(f"  Default: {available[0]}")

        # Update config.py with available browser
        if Path("config.py").exists():
            with open("config.py", "r", encoding="utf-8") as f:
                config_content = f.read()

            # Update browser type
            config_content = config_content.replace(
                "BROWSER_TYPE = \"chrome\"",
                f"BROWSER_TYPE = \"{available[0]}\""
            )

            with open("config.py", "w", encoding="utf-8") as f:
                f.write(config_content)
            print(f"✓ Updated config.py with {available[0]} as default browser")

        return True
    else:
        print("✗ No browser found. Please install Chrome, Firefox, or Edge")
        return False

def verify_installation():
    """Verify installation"""
    print("\n[6/6] Verifying installation...")

    checks = [
        ("account.txt", Path("account.txt").exists()),
        ("config.py", Path("config.py").exists()),
        ("main.py", Path("main.py").exists()),
        ("requirements.txt", Path("requirements.txt").exists()),
        ("logs directory", Path("logs").exists()),
    ]

    all_good = True
    for check_name, exists in checks:
        if exists:
            print(f"✓ {check_name}")
        else:
            print(f"✗ {check_name}")
            all_good = False

    return all_good

def print_footer():
    """Print installation footer"""
    print("\n" + "=" * 60)
    print("SETUP COMPLETE")
    print("=" * 60)

    print("\nNext steps:")
    print("1. Edit account.txt with your email|password list")
    print("2. Configure URLs in config.py if needed")
    print("3. Run the bot:")
    print("   Windows:")
    print("     venv\\Scripts\\python main.py")
    print("   Linux/Mac:")
    print("     ./venv/bin/python main.py")
    print("\nFor headless mode:")
    print("   python main.py --headless")
    print("\nFor help:")
    print("   python main.py --help")

def main():
    """Main setup function"""
    print_header()

    steps = [
        check_python_version,
        create_virtual_env,
        install_dependencies,
        setup_files,
        check_browser,
        verify_installation,
    ]

    success = True
    for step in steps:
        if not step():
            success = False
            break

    if success:
        print_footer()
        return 0
    else:
        print("\n" + "=" * 60)
        print("SETUP FAILED")
        print("=" * 60)
        print("\nPlease fix the errors above and run setup.py again")
        return 1

if __name__ == "__main__":
    sys.exit(main())