# Upgrade ke Playwright v2.0

## Changes
- ✅ Selenium → Playwright (30-40% lebih cepat)
- ✅ Async/await native
- ✅ **Parallel execution** (2 browser sekaligus, ~2x speedup)
- ✅ Auto-waiting lebih bagus (less timeout)
- ✅ Semua logic tetap sama (9router, remove account, dll)

## Installation

```bash
# Install dependencies aja (ga perlu download browser!)
pip install -r requirements.txt

# Run bot (pakai Chrome/Edge sistem kamu)
python main.py

# Run headless
python main.py --headless
```

**Note:** Bot otomatis pakai Chrome sistem kamu. Kalau Chrome ga ada, fallback ke Edge.

## Config Parallel

Edit `config.py`:
```python
PARALLEL_BROWSERS = 2  # 2-3 recommended (balance speed vs resource)
```

**Warning:** Jangan set terlalu tinggi:
- Memory usage: ~500MB per browser
- Google bisa detect mass login dari IP sama
- 9router API rate limit

## Performance

**Before (Selenium sequential):**
- 2 akun = ~4-5 menit (60-75 detik per akun)

**After (Playwright parallel x2):**
- 2 akun = ~2-2.5 menit (~50% faster)
- 10 akun = ~8-10 menit (vs 15-20 menit sebelumnya)
