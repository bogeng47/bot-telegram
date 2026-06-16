import requests
import logging
from config import TG_BOT_TOKEN, TG_CHAT_ID

log = logging.getLogger(__name__)


def _send(text: str) -> None:
    """Kirim pesan ke Telegram. Gagal silent — tidak menghentikan bot."""
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        log.warning("Telegram token/chat ID belum diset, notifikasi dilewat.")
        return
    try:
        url = f"https://api.telegram.org/bot8884721906:AAE78KtXG537ibgZx1R7dPU6C-zKd1aC6sE/sendMessage"
        requests.post(url, json={
            "chat_id": 6759429554,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }, timeout=10)
    except Exception as e:
        log.error(f"Gagal kirim notif Telegram: {e}")


def notify_success(project: str, chain: str, price: str,
                   wallet: str, tx_hash: str, explorer_url: str) -> None:
    short_wallet = f"{wallet[:6]}...{wallet[-4:]}"
    short_tx     = f"{tx_hash[:10]}...{tx_hash[-6:]}"
    text = (
        "✅ <b>MINT SUKSES</b>\n\n"
        f"🎨 <b>Project</b>  : {project}\n"
        f"⛓️ <b>Chain</b>    : {chain.capitalize()}\n"
        f"💰 <b>Harga</b>    : {price}\n"
        f"👛 <b>Wallet</b>   : {short_wallet}\n"
        f"🔗 <b>Tx Hash</b>  : <code>{short_tx}</code>\n"
        f"🌐 <b>Explorer</b> : {explorer_url}/{tx_hash}"
    )
    _send(text)
    log.info(f"Notifikasi sukses dikirim — {tx_hash}")


def notify_failed(project: str, chain: str, reason: str,
                  retry: int, max_retry: int) -> None:
    text = (
        "❌ <b>MINT GAGAL</b>\n\n"
        f"🎨 <b>Project</b> : {project}\n"
        f"⛓️ <b>Chain</b>   : {chain.capitalize()}\n"
        f"⚠️ <b>Alasan</b>  : {reason}\n\n"
        f"🔄 Retry ke-{retry} dari {max_retry}..."
    )
    _send(text)
    log.warning(f"Notifikasi gagal dikirim — retry {retry}/{max_retry}")


def notify_aborted(project: str, chain: str, reason: str) -> None:
    text = (
        "🚫 <b>MINT DIBATALKAN</b>\n\n"
        f"🎨 <b>Project</b> : {project}\n"
        f"⛓️ <b>Chain</b>   : {chain.capitalize()}\n"
        f"⚠️ <b>Alasan</b>  : {reason}"
    )
    _send(text)
    log.error(f"Notifikasi abort dikirim — {reason}")


def notify_standby(project: str, chain: str, start_time: str) -> None:
    text = (
        "⏳ <b>STANDBY MODE</b>\n\n"
        f"🎨 <b>Project</b>    : {project}\n"
        f"⛓️ <b>Chain</b>      : {chain.capitalize()}\n"
        f"🕐 <b>Jadwal Mint</b> : {start_time}\n\n"
        "Bot mulai polling kontrak..."
    )
    _send(text)
