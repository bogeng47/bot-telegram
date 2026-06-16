import asyncio
import json
import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from web3 import Web3

from config import CHAINS, POLL_INTERVAL, STANDBY_BEFORE_MINUTES

log = logging.getLogger(__name__)

# Load ABI
import os
ABI_PATH = os.path.join(os.path.dirname(__file__), "abi", "common_mint.json")
with open(ABI_PATH) as f:
    # Filter komentar (bukan entry ABI valid)
    COMMON_ABI = [x for x in json.load(f) if "comment" not in x]


def get_web3(chain: str) -> Web3:
    """Buat koneksi Web3 ke chain yang dipilih."""
    chain_cfg = CHAINS.get(chain)
    if not chain_cfg:
        raise ValueError(f"Chain '{chain}' tidak dikenal. Pilih dari: {list(CHAINS.keys())}")
    w3 = Web3(Web3.HTTPProvider(chain_cfg["rpc"]))
    if not w3.is_connected():
        raise ConnectionError(f"Gagal connect ke RPC {chain}: {chain_cfg['rpc']}")
    return w3


def check_sale_active(w3: Web3, contract_address: str, function_name: str) -> bool:
    """
    Panggil fungsi view kontrak untuk cek apakah sale sudah aktif.
    Kalau fungsi tidak ada di kontrak, raise AttributeError.
    """
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(contract_address),
        abi=COMMON_ABI,
    )
    fn = getattr(contract.functions, function_name, None)
    if fn is None:
        raise AttributeError(
            f"Fungsi '{function_name}' tidak ditemukan di ABI. "
            "Pastikan nama fungsi sudah benar atau tambahkan ABI manual."
        )
    return fn().call()


def parse_start_time(start_time_str: str, tz_str: str) -> datetime:
    """Parse string jadwal ke datetime object dengan timezone."""
    tz = ZoneInfo(tz_str)
    dt = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
    return dt.replace(tzinfo=tz)


async def wait_until_standby(start_dt: datetime, project_name: str) -> None:
    """
    Idle sampai H-STANDBY_BEFORE_MINUTES dari jadwal.
    Setelah itu return untuk mulai polling.
    """
    standby_seconds = STANDBY_BEFORE_MINUTES * 60
    while True:
        now = datetime.now(tz=start_dt.tzinfo)
        remaining = (start_dt - now).total_seconds()

        if remaining <= standby_seconds:
            log.info(f"[{project_name}] Masuk standby mode — {remaining:.0f}s sebelum jadwal.")
            return

        # Log setiap 10 menit saat idle
        log.info(f"[{project_name}] Menunggu... {remaining/60:.1f} menit lagi.")
        await asyncio.sleep(60)


async def poll_until_active(
    w3: Web3,
    contract_address: str,
    sale_fn: str,
    project_name: str,
    start_dt: datetime,
) -> None:
    """
    Polling kontrak tiap POLL_INTERVAL detik.
    Return begitu sale aktif atau jadwal sudah lewat > 30 menit (timeout).
    """
    timeout_seconds = 30 * 60  # 30 menit timeout setelah jadwal
    log.info(f"[{project_name}] Mulai polling '{sale_fn}' tiap {POLL_INTERVAL}s...")

    while True:
        try:
            active = check_sale_active(w3, contract_address, sale_fn)
            if active:
                log.info(f"[{project_name}] Sale AKTIF! Lanjut mint.")
                return
        except Exception as e:
            log.warning(f"[{project_name}] Error saat polling: {e}")

        # Cek timeout
        now = datetime.now(tz=start_dt.tzinfo)
        elapsed = (now - start_dt).total_seconds()
        if elapsed > timeout_seconds:
            raise TimeoutError(
                f"Sale tidak aktif setelah {timeout_seconds//60} menit dari jadwal. "
                "Kemungkinan jadwal berubah atau kontrak berbeda."
            )

        await asyncio.sleep(POLL_INTERVAL)
