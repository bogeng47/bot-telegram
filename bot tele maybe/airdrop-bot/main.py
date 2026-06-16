import asyncio
import logging
import os

from config import DB_PATH
from database import init_db
from scheduler import run_all, start_scheduler

log = logging.getLogger(__name__)


async def main():
    # Buat folder data kalau belum ada
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Inisialisasi database
    await init_db()
    log.info("Database siap.")

    # Jalanin sekali langsung, lalu aktifkan scheduler
    await run_all()
    scheduler = start_scheduler()

    try:
        # Keep alive
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        log.info("Bot dihentikan.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    asyncio.run(main())
