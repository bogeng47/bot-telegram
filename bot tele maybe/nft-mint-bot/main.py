"""
NFT Mint Bot — Entry Point

Usage:
    python main.py targets/target_example.json
    python main.py targets/my_project.json
"""

import asyncio
import json
import logging
import sys
from datetime import datetime

from config import CHAINS, PRIVATE_KEY
from monitor import get_web3, parse_start_time, wait_until_standby, poll_until_active
from minter import execute_mint
from notifier import notify_standby, notify_success, notify_failed, notify_aborted

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def validate_config() -> None:
    """Cek .env sudah diisi dengan benar."""
    if not PRIVATE_KEY or PRIVATE_KEY == "0xyour_private_key_here":
        raise ValueError("PRIVATE_KEY belum diset di .env!")


def load_target(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


async def run(target: dict) -> None:
    project = target["project_name"]
    chain   = target["chain"]

    if chain not in CHAINS:
        raise ValueError(f"Chain '{chain}' tidak dikenal. Pilih dari: {list(CHAINS.keys())}")

    # Parse jadwal
    schedule   = target.get("schedule", {})
    start_time = schedule.get("start_time")
    tz_str     = schedule.get("timezone", "Asia/Jakarta")

    if start_time:
        start_dt = parse_start_time(start_time, tz_str)
        log.info(f"[{project}] Jadwal mint: {start_dt.strftime('%d %b %Y %H:%M:%S %Z')}")
    else:
        # Tidak ada jadwal → langsung polling
        from datetime import timezone
        start_dt = datetime.now(tz=__import__('zoneinfo').ZoneInfo(tz_str))
        log.info(f"[{project}] Tidak ada jadwal, langsung polling...")

    # Connect Web3
    log.info(f"[{project}] Connecting ke {chain.capitalize()}...")
    w3 = get_web3(chain)
    log.info(f"[{project}] Connected. Block: {w3.eth.block_number}")

    # Fase 1: idle sampai standby window
    if start_time:
        await wait_until_standby(start_dt, project)
        notify_standby(project, chain, start_dt.strftime("%d %b %Y %H:%M:%S %Z"))

    # Fase 2: polling kontrak sampai sale aktif
    sale_fn = target["sale_check"]["function_name"]
    try:
        await poll_until_active(w3, target["contract_address"], sale_fn, project, start_dt)
    except TimeoutError as e:
        notify_aborted(project, chain, str(e))
        log.error(f"[{project}] Timeout: {e}")
        return

    # Fase 3: eksekusi mint
    success, tx_hash, error = await execute_mint(w3, target)

    chain_cfg = CHAINS[chain]
    from web3 import Web3
    from config import PRIVATE_KEY
    account = w3.eth.account.from_key(PRIVATE_KEY)
    wallet  = account.address

    price_str = f"{float(target['mint']['price_eth']) * target['mint']['quantity']} ETH"

    if success:
        notify_success(
            project, chain, price_str,
            wallet, tx_hash, chain_cfg["explorer"]
        )
    else:
        from config import MAX_RETRY
        notify_aborted(project, chain, error or "Semua retry gagal")


async def main() -> None:
    validate_config()

    if len(sys.argv) < 2:
        print("Usage: python main.py targets/your_target.json")
        print("Contoh: python main.py targets/target_example.json")
        sys.exit(1)

    target_path = sys.argv[1]
    log.info(f"Loading target: {target_path}")
    target = load_target(target_path)

    log.info(f"=== NFT MINT BOT ===")
    log.info(f"Project : {target['project_name']}")
    log.info(f"Chain   : {target['chain'].capitalize()}")
    log.info(f"Contract: {target['contract_address']}")

    await run(target)


if __name__ == "__main__":
    asyncio.run(main())
