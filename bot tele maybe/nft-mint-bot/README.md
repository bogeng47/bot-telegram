# NFT Mint Bot

Bot otomatis mint NFT — monitor jadwal + konfirmasi kontrak, lalu eksekusi mint dan kirim notifikasi ke Telegram.

## Struktur

```
nft-mint-bot/
├── main.py                  ← Entry point
├── config.py                ← Chains, wallet, settings
├── monitor.py               ← Polling kontrak + timing
├── minter.py                ← Eksekusi transaksi mint
├── notifier.py              ← Notifikasi Telegram
├── requirements.txt
├── .env.example             ← Template konfigurasi
├── targets/
│   └── target_example.json  ← Template target mint
└── abi/
    └── common_mint.json     ← ABI fungsi mint umum
```

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Buat file .env
```bash
copy .env.example .env
```
Isi:
- `PRIVATE_KEY` — private key wallet kamu
- `INFURA_KEY` — dari https://infura.io (atau biarkan kosong untuk chain yang punya public RPC)
- `TG_BOT_TOKEN` — dari @BotFather
- `TG_CHAT_ID` — cek via @userinfobot

### 3. Buat file target
Copy `targets/target_example.json` → buat file baru per project:

```json
{
  "project_name": "Nama Project NFT",
  "chain": "ethereum",
  "contract_address": "0xABC...",

  "mint": {
    "function_name": "mint",
    "quantity": 1,
    "price_eth": "0.08",
    "merkle_proof": []
  },

  "sale_check": {
    "function_name": "saleIsActive"
  },

  "schedule": {
    "start_time": "2025-01-20 20:00:00",
    "timezone": "Asia/Jakarta"
  },

  "gas": {
    "max_fee_gwei": 50,
    "priority_fee_gwei": 2
  }
}
```

### 4. Jalankan
```bash
python main.py targets/nama_project.json
```

## Chain yang Didukung

| Key | Network |
|---|---|
| `ethereum` | Ethereum Mainnet |
| `polygon` | Polygon |
| `base` | Base |
| `arbitrum` | Arbitrum One |
| `optimism` | Optimism |
| `bsc` | BNB Smart Chain |
| `avalanche` | Avalanche C-Chain |

## Fungsi Mint yang Didukung

| function_name | Keterangan |
|---|---|
| `mint` | mint(uint256 quantity) |
| `mintNFT` | mintNFT(uint256 numberOfTokens) |
| `whitelistMint` | whitelistMint(uint256 qty, bytes32[] proof) |
| `presaleMint` | presaleMint(bytes32[] proof, uint256 qty) |

Kalau fungsi kontrak berbeda, tambahkan ABI-nya ke `abi/common_mint.json`.

## Fungsi Cek Sale yang Didukung

- `saleIsActive`
- `mintingOpen`
- `publicSaleActive`
- `whitelistSaleActive`

## Flow Bot

```
Input target JSON
      │
      ▼
Idle sampai H-5 menit dari jadwal
      │
      ▼
Standby: polling kontrak tiap 3 detik
      │
      ▼
Sale aktif? → Eksekusi mint transaction
      │
      ▼
Notifikasi Telegram (sukses/gagal)
```
