import os
from dotenv import load_dotenv

load_dotenv()

# ── Wallet ────────────────────────────────────────────────
PRIVATE_KEY: str = os.getenv("PRIVATE_KEY", "")

# ── Telegram ──────────────────────────────────────────────
TG_BOT_TOKEN: str = os.getenv("TG_BOT_TOKEN", "")
TG_CHAT_ID: str   = os.getenv("TG_CHAT_ID", "")

# ── Setting ───────────────────────────────────────────────
POLL_INTERVAL: int            = int(os.getenv("POLL_INTERVAL", 3))
STANDBY_BEFORE_MINUTES: int   = int(os.getenv("STANDBY_BEFORE_MINUTES", 5))
MAX_RETRY: int                = int(os.getenv("MAX_RETRY", 3))

# ── EVM Chains ────────────────────────────────────────────
INFURA_KEY = os.getenv("INFURA_KEY", "")

CHAINS: dict[str, dict] = {
    "ethereum": {
        "rpc": f"https://mainnet.infura.io/v3/{INFURA_KEY}",
        "explorer": "https://etherscan.io/tx",
        "chain_id": 1,
    },
    "polygon": {
        "rpc": f"https://polygon-mainnet.infura.io/v3/{INFURA_KEY}",
        "explorer": "https://polygonscan.com/tx",
        "chain_id": 137,
    },
    "base": {
        "rpc": "https://mainnet.base.org",
        "explorer": "https://basescan.org/tx",
        "chain_id": 8453,
    },
    "arbitrum": {
        "rpc": "https://arb1.arbitrum.io/rpc",
        "explorer": "https://arbiscan.io/tx",
        "chain_id": 42161,
    },
    "optimism": {
        "rpc": "https://mainnet.optimism.io",
        "explorer": "https://optimistic.etherscan.io/tx",
        "chain_id": 10,
    },
    "bsc": {
        "rpc": "https://bsc-dataseed.binance.org",
        "explorer": "https://bscscan.com/tx",
        "chain_id": 56,
    },
    "avalanche": {
        "rpc": "https://api.avax.network/ext/bc/C/rpc",
        "explorer": "https://snowtrace.io/tx",
        "chain_id": 43114,
    },
}
