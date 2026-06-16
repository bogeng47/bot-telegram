#!/bin/bash
# =============================================================
# Upload file bot ke VPS via SCP
# Edit VPS_USER dan VPS_IP sesuai VPS kamu
# Jalankan dari folder "bot tele maybe" di laptop
# Usage: bash deploy/upload.sh
# =============================================================

VPS_USER="root"          # ganti dengan user VPS kamu
VPS_IP="IP vps mu"     # ganti dengan IP VPS kamu
REMOTE_DIR="root/bots"

echo "=== Upload ke VPS $VPS_USER@$VPS_IP ==="

# Upload kedua folder bot
scp -r airdrop-bot "$VPS_USER@$VPS_IP:$REMOTE_DIR/"
scp -r nft-mint-bot "$VPS_USER@$VPS_IP:$REMOTE_DIR/"

echo ""
echo "✅ Upload selesai!"
echo ""
echo "Langkah selanjutnya:"
echo "  1. ssh $VPS_USER@$VPS_IP"
echo "  2. cd ~/bots"
echo "  3. bash deploy/setup.sh"
echo "  4. Isi .env di masing-masing folder bot"
echo "  5. bash deploy/install-services.sh"
