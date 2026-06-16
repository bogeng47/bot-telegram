"""
Jalanin script ini sekali untuk tambah akun Telegram baru.
Telethon akan minta nomor HP dan kode OTP, lalu simpan session-nya.

Usage:
    python accounts/add_account.py
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import aiosqlite
from telethon import TelegramClient
from config import API_ID, API_HASH, SESSION_DIR, DB_PATH


async def add_account():
    os.makedirs(SESSION_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    phone = input("Masukkan nomor HP (format: +628xxx): ").strip()
    session_path = os.path.join(SESSION_DIR, phone.replace("+", ""))

    client = TelegramClient(session_path, API_ID, API_HASH)
    await client.start(phone=phone)

    me = await client.get_me()
    print(f"Login berhasil sebagai: {me.first_name} ({me.phone})")

    # Simpan ke database
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                phone       TEXT UNIQUE NOT NULL,
                session     TEXT NOT NULL,
                is_active   INTEGER DEFAULT 1,
                created_at  TEXT DEFAULT (datetime('now'))
            )
        """)
        await db.execute(
            "INSERT OR IGNORE INTO accounts (phone, session) VALUES (?, ?)",
            (phone, session_path),
        )
        await db.commit()

    print(f"Akun {phone} berhasil ditambahkan ke database.")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(add_account())
