import aiosqlite
from config import DB_PATH


async def init_db():
    """Buat tabel kalau belum ada."""
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
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_name    TEXT NOT NULL,
                bot_username TEXT NOT NULL,
                description TEXT,
                is_active   INTEGER DEFAULT 1
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS claim_history (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id  INTEGER NOT NULL,
                task_id     INTEGER NOT NULL,
                status      TEXT NOT NULL,  -- 'success' | 'failed' | 'skipped'
                note        TEXT,
                claimed_at  TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (account_id) REFERENCES accounts(id),
                FOREIGN KEY (task_id)    REFERENCES tasks(id)
            )
        """)
        await db.commit()


async def get_active_accounts():
    """Ambil semua akun yang aktif."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM accounts WHERE is_active = 1"
        ) as cursor:
            return await cursor.fetchall()


async def get_active_tasks():
    """Ambil semua task yang aktif."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM tasks WHERE is_active = 1"
        ) as cursor:
            return await cursor.fetchall()


async def log_claim(account_id: int, task_id: int, status: str, note: str = ""):
    """Simpan hasil claim ke history."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO claim_history (account_id, task_id, status, note) VALUES (?, ?, ?, ?)",
            (account_id, task_id, status, note),
        )
        await db.commit()


async def already_claimed_today(account_id: int, task_id: int) -> bool:
    """Cek apakah akun sudah claim task ini hari ini."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT id FROM claim_history
            WHERE account_id = ? AND task_id = ?
              AND date(claimed_at) = date('now')
              AND status = 'success'
            """,
            (account_id, task_id),
        ) as cursor:
            return await cursor.fetchone() is not None
