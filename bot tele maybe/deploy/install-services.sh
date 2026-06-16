#!/bin/bash
# =============================================================
# Install systemd services untuk airdrop-bot & nft-mint-bot
# Jalankan: bash install-services.sh
# =============================================================

set -e

BOT_USER=$(whoami)
BOTS_DIR="$HOME/bots"

# ── airdrop-bot service ───────────────────────────────────────
echo "=== Install service: airdrop-bot ==="
sudo tee /etc/systemd/system/airdrop-bot.service > /dev/null <<EOF
[Unit]
Description=Telegram Airdrop Bot
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$BOT_USER
WorkingDirectory=$BOTS_DIR/airdrop-bot
ExecStart=$BOTS_DIR/airdrop-bot/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# ── nft-mint-bot — tidak pakai service permanen ───────────────
# nft-mint-bot dijalankan manual per target via screen/tmux
# karena butuh argumen file target yang berbeda-beda

echo ""
echo "=== Setup tmux untuk nft-mint-bot ==="
sudo apt install -y tmux

echo ""
echo "=== Enable & start airdrop-bot ==="
sudo systemctl daemon-reload
sudo systemctl enable airdrop-bot
sudo systemctl start airdrop-bot

echo ""
echo "✅ Selesai!"
echo ""
echo "Perintah berguna:"
echo "  sudo systemctl status airdrop-bot    → cek status"
echo "  sudo journalctl -u airdrop-bot -f    → lihat log live"
echo "  sudo systemctl restart airdrop-bot   → restart"
echo "  sudo systemctl stop airdrop-bot      → stop"
