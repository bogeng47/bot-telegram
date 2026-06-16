# Airdrop Bot

Bot otomatis untuk mengerjakan task airdrop di Telegram.

## Struktur

```
airdrop-bot/
├── main.py                  # Entry point
├── config.py                # Konfigurasi (API keys, path, interval)
├── database.py              # Handler SQLite
├── scheduler.py             # Scheduler & runner per akun
├── requirements.txt         # Dependencies
├── .env.example             # Template environment variables
├── accounts/
│   ├── add_account.py       # Script untuk tambah akun baru
│   └── sessions/            # File session Telethon (auto-generated)
├── bots/
│   ├── __init__.py          # Daftar bot yang aktif
│   ├── base_bot.py          # Class dasar untuk semua bot
│   └── bot_example.py       # Template bot — copy untuk bot baru
└── data/
    └── airdrop.db           # Database SQLite (auto-generated)
```

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Buat file .env
```bash
copy .env.example .env
```
Isi `API_ID` dan `API_HASH` dari https://my.telegram.org

### 3. Tambah akun Telegram
```bash
python accounts/add_account.py
```
Ikuti instruksi: masukkan nomor HP dan kode OTP.

### 4. Tambah bot airdrop baru
- Copy `bots/bot_example.py` → misal `bots/bot_hamster.py`
- Ganti `BOT_NAME`, `BOT_USERNAME`
- Isi logika di `run_task()`
- Daftarkan di `bots/__init__.py`:
  ```python
  from bots.bot_hamster import HamsterBot
  REGISTERED_BOTS = [HamsterBot]
  ```

### 5. Jalankan
```bash
python main.py
```

## Database Tables

| Tabel | Isi |
|---|---|
| `accounts` | Data akun Telegram |
| `tasks` | Daftar bot/task airdrop |
| `claim_history` | Riwayat hasil claim per akun per task |
