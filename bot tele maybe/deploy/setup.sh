#!/bin/bash
# =============================================================
# Setup script untuk VPS Ubuntu/Debian
# Jalankan: bash setup.sh
# =============================================================

set -e

echo "=== Update system ==="
sudo apt update && sudo apt upgrade -y

echo "=== Install Python & pip ==="
sudo apt install -y python3 python3-pip python3-venv git

echo "=== Buat folder project ==="
mkdir -p ~/bots
cd ~/bots

echo "=== Setup airdrop-bot ==="
cd ~/bots
# Upload folder airdrop-bot kamu ke sini via scp/sftp dulu
# Lalu:
python3 -m venv airdrop-bot/venv
source airdrop-bot/venv/bin/activate
pip install -r airdrop-bot/requirements.txt
deactivate

echo "=== Setup nft-mint-bot ==="
python3 -m venv nft-mint-bot/venv
source nft-mint-bot/venv/bin/activate
pip install -r nft-mint-bot/requirements.txt
deactivate

echo "=== Selesai! Lanjut jalankan: bash install-services.sh ==="
