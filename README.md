# 🤖 Telegram Airdrop & NFT Mint Bot

Dua bot otomatis dalam satu repo:
- **airdrop-bot** — kerjakan task airdrop di Telegram secara otomatis
- **nft-mint-bot** — auto mint NFT saat whitelist/guaranteed mint window buka

---

## 📦 Struktur Repo

```
├── airdrop-bot/         ← Bot airdrop Telegram
├── nft-mint-bot/        ← Bot mint NFT on-chain
├── deploy/              ← Script deploy ke VPS
├── .gitignore
└── README.md
```

---

## 🤖 Airdrop Bot

Bot otomatis untuk mengerjakan task airdrop di Telegram. Support bot chat biasa maupun Mini App (WebApp).

### Fitur
- **Multi-bot** — jalankan banyak bot airdrop sekaligus
- **WebApp support** — buka Mini App via Playwright headless browser
- **Auto-detect tombol** — cari tombol Claim/Farm/Collect otomatis tanpa hardcode
- **Multi-akun** — banyak akun Telegram jalan paralel
- **Scheduler** — task otomatis berulang tiap X menit
- **Database** — tracking history claim, hindari double claim

### Setup
```bash
cd airdrop-bot
pip install -r requirements.txt
python -m playwright install chromium

cp .env.example .env
# isi API_ID & API_HASH dari https://my.telegram.org

python accounts/add_account.py
python main.py
```

### Tambah Bot Baru
1. Copy `airdrop-bot/bots/bot_example.py` → `bots/bot_NAMA.py`
2. Isi `BOT_NAME`, `BOT_USERNAME`, set `IS_WEBAPP = True/False`
3. Daftarkan di `bots/__init__.py`

---

## 🎨 NFT Mint Bot

Bot otomatis mint NFT untuk whitelist/guaranteed mint. Monitor jadwal + polling kontrak, eksekusi mint, notifikasi Telegram.

### Fitur
- **Multi-chain EVM** — Ethereum, Polygon, Base, Arbitrum, Optimism, BSC, Avalanche
- **Jadwal + konfirmasi kontrak** — idle → standby H-5 menit → polling tiap 3 detik
- **Whitelist/Merkle proof** — support WL mint dengan proof
- **Auto-retry** — retry otomatis kalau transaksi gagal
- **Notifikasi Telegram** — hasil mint langsung ke HP

### Setup
```bash
cd nft-mint-bot
pip install -r requirements.txt

cp .env.example .env
# isi PRIVATE_KEY, INFURA_KEY, TG_BOT_TOKEN, TG_CHAT_ID
```

### Jalankan per target
```bash
# Copy & edit file target
cp targets/target_example.json targets/nama_project.json
# edit contract address, fungsi mint, jadwal, harga

python main.py targets/nama_project.json
```

---

## 🖥️ Deploy ke VPS (Debian/Ubuntu)

```bash
# Upload ke VPS
scp -r . user@ip-vps:~/bots/

# Di VPS
bash deploy/setup.sh
bash deploy/install-services.sh

# Jalankan nft-mint-bot per target
bash deploy/mint.sh targets/nama_project.json
```

### Kelola airdrop-bot (systemd)
```bash
sudo systemctl status airdrop-bot
sudo journalctl -u airdrop-bot -f    # log live
sudo systemctl restart airdrop-bot
```

### Kelola nft-mint-bot (tmux)
```bash
tmux attach -t mint-nama_project     # lihat log
tmux ls                              # list session
tmux kill-session -t mint-nama_project
```

---

## ⚙️ Environment Variables

### airdrop-bot `.env`
| Key | Keterangan |
|---|---|
| `API_ID` | Dari [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Dari [my.telegram.org](https://my.telegram.org) |
| `TASK_INTERVAL` | Interval task dalam menit (default: 60) |

### nft-mint-bot `.env`
| Key | Keterangan |
|---|---|
| `PRIVATE_KEY` | Private key wallet |
| `INFURA_KEY` | Dari [infura.io](https://infura.io) |
| `TG_BOT_TOKEN` | Dari [@BotFather](https://t.me/BotFather) |
| `TG_CHAT_ID` | Dari [@userinfobot](https://t.me/userinfobot) |

---

## ⚠️ Disclaimer

Penggunaan bot otomatis mungkin melanggar Terms of Service platform terkait. Jaga keamanan private key dan credentials kamu. Gunakan dengan risiko sendiri.
