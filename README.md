# Kiro Registration Bot

Bot otomatis untuk registrasi/login ke Kiro menggunakan Google OAuth dan mengambil refresh token.

## Fitur

- **Async/parallel execution** - 2+ akun berjalan bersamaan (~50% lebih cepat)
- Baca akun dari file `account.txt` (format: `email|password`)
- Login ke Kiro menggunakan Google OAuth melalui browser otomatis
- Ekstrak refresh token dari local storage
- Kirim token ke 9router API
- **Auto-remove** akun yang berhasil dari `account.txt`
- Pakai Chrome/Edge sistem (tidak perlu download browser)
- Mode headless tersedia
- Logging dan monitoring progress dengan color output

## Struktur Project

```
bot-auto-kiro/
├── main.py              # Script utama (async Playwright)
├── config.py            # Konfigurasi
├── account.txt          # Daftar akun (email|password)
├── requirements.txt     # Dependencies Python
├── UPGRADE.md          # Changelog Playwright v2.0
├── logs/               # Log files & screenshots
│   └── .gitkeep
└── README.md           # Dokumentasi
```

## Instalasi

1. Clone atau buat project
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Setup file `account.txt`:

```
contoh@contoh.com|Contohpassword
contoh2@contoh.com|Contohpassword
contoh3@contoh.com|Contohpassword
```

4. Konfigurasi di `config.py`:

- Update URL Kiro sesuai kebutuhan
- Update 9router API endpoint
- Sesuaikan `PARALLEL_BROWSERS` (default: 2)
- Sesuaikan timeout sesuai kebutuhan

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
- `logs/screenshot_*.png` - Screenshots (saat error)
- Console output dengan color-coded progress
- Akun yang berhasil otomatis dihapus dari `account.txt`

## Flow Kerja

1. Baca akun dari `account.txt`
2. Buka browser dan navigasi ke halaman login Kiro
3. Klik tombol login dengan Google
4. Isi email dan password Google
5. Tunggu redirect kembali ke Kiro
6. Ekstrak refresh token dari browser
7. Kirim token ke 9router API
8. Simpan token ke `tokens.json`

## Konfigurasi

Edit `config.py` untuk mengatur:

- `PARALLEL_BROWSERS`: Jumlah browser bersamaan (2-3 recommended)
- `HEADLESS_MODE`: True/False
- `WAIT_TIMEOUT`: Timeout dalam detik
- `TYPING_DELAY`: Delay typing (0 = maksimal speed)
- URLs Kiro dan 9router

## Troubleshooting

### 1. Chrome/Edge tidak ditemukan

- Pastikan Chrome atau Edge terinstall di sistem
- Bot otomatis fallback dari Chrome → Edge

### 2. Browser tidak terbuka

- Coba non-headless mode: `python main.py`
- Check error di `logs/registration.log`

### 3. Gagal login Google

- Pastikan email/password benar di `account.txt`
- Google mungkin memerlukan captcha (gunakan akun verified)
- Cek screenshot di `logs/` untuk debug

### 4. Token tidak ditemukan

- Pastikan login berhasil sampai dashboard Kiro
- Non-headless mode untuk inspect manual
- Cek browser console untuk error JS

### 5. Parallel execution lambat

- Turunkan `PARALLEL_BROWSERS` di config.py
- 2-3 browser optimal (balance speed vs resource)
- Memory usage: ~500MB per browser

## Keamanan

- **JANGAN** commit `account.txt` atau `tokens.json` ke git
- Gunakan `.gitignore` untuk file sensitif
- Data sensitif di-mask di log file

## Performance

**v2.0 (Playwright async + parallel):**

- 2 akun = ~2-2.5 menit
- 10 akun = ~8-10 menit

**v1.0 (Selenium sequential):**

- 2 akun = ~4-5 menit
- 10 akun = ~15-20 menit

**Improvement: ~50% faster** dengan parallel execution

## Catatan

- Script ini menggunakan **Playwright async** untuk otomatisasi browser
- Google mungkin memblokir akun jika terlalu banyak login dari IP sama
- Jangan set `PARALLEL_BROWSERS` terlalu tinggi (2-3 optimal)
- Untuk produksi, pertimbangkan proxy/VPN per browser

## License

MIT
