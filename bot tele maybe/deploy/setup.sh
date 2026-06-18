#!/bin/bash
# =============================================================
# Setup script untuk VPS Debian/Ubuntu
# Jalankan: bash setup.sh
# =============================================================

set -e

echo "=== Update system ==="
sudo apt update && sudo apt upgrade -y

echo "=== Install dependencies sistem ==="
sudo apt install -y \
    python3 python3-pip python3-venv git \
    # Playwright system dependencies
    libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libasound2 libpango-1.0-0 libcairo2 \
    libx11-6 libx11-xcb1 libxcb1 libxext6

echo "=== Buat folder project ==="
mkdir -p ~/bots
cd ~/bots

echo "=== Setup airdrop-bot ==="
cd ~/bots
python3 -m venv airdrop-bot/venv
source airdrop-bot/venv/bin/activate
pip install --upgrade pip
pip install -r airdrop-bot/requirements.txt

echo "=== Install Playwright Chromium ==="
python -m playwright install chromium
deactivate

echo "=== Setup nft-mint-bot ==="
python3 -m venv nft-mint-bot/venv
source nft-mint-bot/venv/bin/activate
pip install --upgrade pip
pip install -r nft-mint-bot/requirements.txt
deactivate

echo ""
echo "✅ Setup selesai!"
echo "Lanjut jalankan: bash deploy/install-services.sh"
