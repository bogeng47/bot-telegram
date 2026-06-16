#!/bin/bash
# =============================================================
# Jalankan nft-mint-bot untuk satu target di tmux session
# Usage: bash mint.sh targets/nama_project.json
# =============================================================

TARGET=${1:-"targets/target_example.json"}
SESSION_NAME="mint-$(basename $TARGET .json)"
BOTS_DIR="$HOME/bots"
BOT_DIR="$BOTS_DIR/nft-mint-bot"

# Cek tmux sudah terinstall
if ! command -v tmux &> /dev/null; then
    echo "tmux belum terinstall. Jalankan: sudo apt install tmux"
    exit 1
fi

# Cek file target ada
if [ ! -f "$BOT_DIR/$TARGET" ]; then
    echo "File target tidak ditemukan: $BOT_DIR/$TARGET"
    exit 1
fi

# Kalau session sudah ada, attach saja
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "Session '$SESSION_NAME' sudah berjalan."
    echo "Attach dengan: tmux attach -t $SESSION_NAME"
    exit 0
fi

echo "=== Menjalankan nft-mint-bot ==="
echo "Target  : $TARGET"
echo "Session : $SESSION_NAME"
echo ""

# Buat tmux session baru dan jalankan bot
tmux new-session -d -s "$SESSION_NAME" \
    "cd $BOT_DIR && source venv/bin/activate && python main.py $TARGET; exec bash"

echo "✅ Bot berjalan di background tmux session: $SESSION_NAME"
echo ""
echo "Perintah berguna:"
echo "  tmux attach -t $SESSION_NAME     → lihat log live"
echo "  tmux ls                          → list semua session"
echo "  Ctrl+B lalu D                    → detach (bot tetap jalan)"
echo "  tmux kill-session -t $SESSION_NAME → stop bot"
