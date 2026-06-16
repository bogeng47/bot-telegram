import asyncio
import logging
from telethon import TelegramClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import API_ID, API_HASH, SESSION_DIR, TASK_INTERVAL_MINUTES
from database import get_active_accounts, log_claim, already_claimed_today
from bots import REGISTERED_BOTS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


async def run_for_account(account: dict):
    """Jalanin semua bot untuk satu akun."""
    phone = account["phone"]
    session_path = account["session"]

    client = TelegramClient(session_path, API_ID, API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        log.warning(f"[{phone}] Sesi tidak valid, skip.")
        await client.disconnect()
        return

    log.info(f"[{phone}] Mulai jalanin {len(REGISTERED_BOTS)} bot...")

    for BotClass in REGISTERED_BOTS:
        bot = BotClass(client)
        task_id = None  # TODO: ambil dari DB kalau sudah ada data tasks

        # Skip kalau sudah claim hari ini
        if task_id and await already_claimed_today(account["id"], task_id):
            log.info(f"[{phone}] [{bot.BOT_NAME}] Sudah claim hari ini, skip.")
            continue

        log.info(f"[{phone}] [{bot.BOT_NAME}] Menjalankan task...")
        success, note = await bot.run_task()

        status = "success" if success else "failed"
        log.info(f"[{phone}] [{bot.BOT_NAME}] {status.upper()} — {note}")

        if task_id:
            await log_claim(account["id"], task_id, status, note)

        await asyncio.sleep(3)  # jeda antar bot

    await client.disconnect()


async def run_all():
    """Ambil semua akun aktif dan jalanin task mereka."""
    accounts = await get_active_accounts()
    if not accounts:
        log.warning("Tidak ada akun aktif di database.")
        return

    log.info(f"Menjalankan task untuk {len(accounts)} akun...")
    tasks = [run_for_account(dict(acc)) for acc in accounts]
    await asyncio.gather(*tasks)
    log.info("Semua task selesai.")


def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_all, "interval", minutes=TASK_INTERVAL_MINUTES)
    scheduler.start()
    log.info(f"Scheduler aktif — task tiap {TASK_INTERVAL_MINUTES} menit.")
    return scheduler
