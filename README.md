# Kiro Registration Bot

Bot otomatis untuk registrasi/login ke Kiro menggunakan Google OAuth dan mengambil refresh token.

## Fitur
- Baca akun dari file `account.txt` (format: `email|password`)
- Login ke Kiro menggunakan Google OAuth melalui browser otomatis
- Ekstrak refresh token dari local storage/cookies
- Kirim token ke 9router API
- Support multiple browser (Chrome, Firefox, Edge)
- Mode headless tersedia
- Logging dan monitoring progress

## Struktur Project
```
bot-auto-kiro/
├── main.py              # Script utama
├── config.py            # Konfigurasi
├── account.txt          # Daftar akun (email|password)
├── requirements.txt     # Dependencies Python
├── utils/
│   └── helpers.py      # Helper functions
├── logs/               # Log files
└── README.md           # Dokumentasi
```

## Instalasi

1. Clone atau buat project
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download browser driver (otomatis via webdriver-manager):
```bash
# Chrome driver akan diinstall otomatis
```

4. Setup file `account.txt`:
```
kelxt1@lamakau.com|Blokgamau123
kelxt2@lamakau.com|Blokgamau123
kelxt3@lamakau.com|Blokgamau123
```

5. Konfigurasi di `config.py`:
- Update URL Kiro sesuai kebutuhan
- Update 9router API endpoint
- Sesuaikan timeout dan browser settings

## Penggunaan

### Basic usage:
```bash
python main.py
```

### Mode headless (tidak tampil browser):
```bash
python main.py --headless
```

### Help:
```bash
python main.py --help
```

## Output
- `tokens.json` - Refresh token yang berhasil diekstrak
- `logs/registration.log` - Log file
- Console output dengan progress bar

## Flow Kerja
1. Baca akun dari `account.txt`
2. Buka browser dan navigasi ke halaman login Kiro
3. Klik tombol login dengan Google
4. Isi email dan password Google
5. Tunggu redirect kembali ke Kiro
6. Ekstrak refresh token dari browser
7. Kirim token ke 9router API
8. Simpan token ke `tokens.json`

## Konfigurasi Browser
Edit `config.py` untuk mengatur:
- `BROWSER_TYPE`: chrome, firefox, atau edge
- `HEADLESS_MODE`: True/False
- `WAIT_TIMEOUT`: Timeout dalam detik
- URLs Kiro dan 9router

## Troubleshooting

### 1. Chrome driver tidak ditemukan
```bash
pip install webdriver-manager --upgrade
```

### 2. Browser tidak terbuka
- Pastikan browser terinstall
- Coba non-headless mode dulu: `python main.py`

### 3. Gagal login Google
- Pastikan email/password benar
- Google mungkin memerlukan captcha (gunakan akun baru/verified)
- Tambahkan delay: ubah `time.sleep()` di kode

### 4. Token tidak ditemukan
- Cek apakah Kiro menyimpan token di local storage/cookies
- Debug: non-headless mode dan inspect browser manual

## Keamanan
- **JANGAN** commit `account.txt` atau `tokens.json` ke git
- Gunakan `.gitignore` untuk file sensitif
- Data sensitif di-mask di log file

## Catatan
- Script ini menggunakan Selenium untuk otomatisasi browser
- Google mungkin memblokir akun jika terlalu banyak login cepat
- Rekomendasi: tambahkan delay antar akun (diatur di `config.py`)
- Untuk produksi, pertimbangkan menggunakan proxy/VPN

## License
MIT