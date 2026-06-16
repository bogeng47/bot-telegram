# Deploy ke VPS

## Struktur deploy

```
deploy/
├── upload.sh            ← upload file ke VPS dari laptop
├── setup.sh             ← install Python & dependencies di VPS
├── install-services.sh  ← install systemd service (airdrop-bot)
└── mint.sh              ← jalankan nft-mint-bot per target
```

---

## Step by Step

### Di laptop — upload ke VPS
```bash
# Edit dulu VPS_USER dan VPS_IP di deploy/upload.sh
bash deploy/upload.sh
```

### Di VPS — setup awal (sekali saja)
```bash
ssh user@ip-vps-kamu
cd ~/bots

# Install dependencies
bash deploy/setup.sh

# Isi .env masing-masing bot
cp airdrop-bot/.env.example airdrop-bot/.env
nano airdrop-bot/.env

cp nft-mint-bot/.env.example nft-mint-bot/.env
nano nft-mint-bot/.env

# Tambah akun Telegram untuk airdrop-bot
cd airdrop-bot
source venv/bin/activate
python accounts/add_account.py
deactivate
cd ..

# Install & start service
bash deploy/install-services.sh
```

---

## Mengelola airdrop-bot (systemd)

```bash
# Cek status
sudo systemctl status airdrop-bot

# Lihat log live
sudo journalctl -u airdrop-bot -f

# Restart
sudo systemctl restart airdrop-bot

# Stop
sudo systemctl stop airdrop-bot
```

Bot otomatis restart kalau crash, dan otomatis jalan lagi kalau VPS reboot.

---

## Menjalankan nft-mint-bot per target

```bash
# Dari folder ~/bots di VPS
bash deploy/mint.sh targets/nama_project.json

# Lihat log live
tmux attach -t mint-nama_project

# Detach (bot tetap jalan di background)
# Tekan Ctrl+B lalu D

# List semua session yang berjalan
tmux ls

# Stop bot
tmux kill-session -t mint-nama_project
```

---

## Kenapa airdrop-bot pakai systemd, nft-mint-bot pakai tmux?

| | airdrop-bot | nft-mint-bot |
|---|---|---|
| Jalan | Terus-menerus | Per target, sampai mint selesai |
| Argumen | Tidak butuh | Butuh file target JSON |
| Auto-restart | ✅ systemd | Manual (mint selesai = stop) |
| Cocok untuk | Service permanen | Task sekali jalan |
