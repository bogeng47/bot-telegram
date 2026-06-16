import json
import logging
import os
from web3 import Web3
from eth_account import Account

from config import PRIVATE_KEY, CHAINS, MAX_RETRY

log = logging.getLogger(__name__)

ABI_PATH = os.path.join(os.path.dirname(__file__), "abi", "common_mint.json")
with open(ABI_PATH) as f:
    COMMON_ABI = [x for x in json.load(f) if "comment" not in x]


def get_wallet(w3: Web3) -> tuple[Account, str]:
    """Return (account object, address)."""
    account = w3.eth.account.from_key(PRIVATE_KEY)
    return account, account.address


def build_mint_tx(
    w3: Web3,
    contract_address: str,
    mint_cfg: dict,
    sender: str,
    gas_cfg: dict,
) -> dict:
    """
    Bangun transaksi mint berdasarkan config target.
    Support: mint(qty), mintNFT(qty), whitelistMint(qty, proof), presaleMint(proof, qty)
    """
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(contract_address),
        abi=COMMON_ABI,
    )

    fn_name    = mint_cfg["function_name"]
    quantity   = mint_cfg["quantity"]
    price_wei  = w3.to_wei(mint_cfg["price_eth"], "ether")
    proof      = mint_cfg.get("merkle_proof", [])
    # Convert proof strings ke bytes32
    proof_bytes = [bytes.fromhex(p.replace("0x", "")) for p in proof] if proof else []

    fn = getattr(contract.functions, fn_name, None)
    if fn is None:
        raise AttributeError(f"Fungsi '{fn_name}' tidak ada di ABI.")

    # Build args sesuai nama fungsi
    if fn_name in ("mint", "mintNFT"):
        call = fn(quantity)
    elif fn_name == "whitelistMint":
        call = fn(quantity, proof_bytes)
    elif fn_name == "presaleMint":
        call = fn(proof_bytes, quantity)
    else:
        # Fallback: coba passing quantity saja
        call = fn(quantity)

    nonce = w3.eth.get_transaction_count(sender)
    chain_id = w3.eth.chain_id

    tx = call.build_transaction({
        "from":     sender,
        "value":    price_wei * quantity,
        "nonce":    nonce,
        "chainId":  chain_id,
        "maxFeePerGas":         w3.to_wei(gas_cfg.get("max_fee_gwei", 50), "gwei"),
        "maxPriorityFeePerGas": w3.to_wei(gas_cfg.get("priority_fee_gwei", 2), "gwei"),
    })

    return tx


def send_mint_tx(w3: Web3, tx: dict, account: Account) -> str:
    """Sign dan broadcast transaksi. Return tx hash."""
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return tx_hash.hex()


async def execute_mint(
    w3: Web3,
    target: dict,
) -> tuple[bool, str, str]:
    """
    Eksekusi mint dengan retry.

    Returns:
        (success, tx_hash_or_empty, error_message)
    """
    import asyncio

    account, address = get_wallet(w3)
    chain    = target["chain"]
    chain_cfg = CHAINS[chain]
    project  = target["project_name"]

    log.info(f"[{project}] Wallet: {address}")
    log.info(f"[{project}] Mulai mint di {chain.capitalize()}...")

    for attempt in range(1, MAX_RETRY + 1):
        try:
            tx = build_mint_tx(
                w3,
                target["contract_address"],
                target["mint"],
                address,
                target.get("gas", {}),
            )
            tx_hash = send_mint_tx(w3, tx, account)

            log.info(f"[{project}] Tx terkirim: {tx_hash}")
            log.info(f"[{project}] Explorer: {chain_cfg['explorer']}/{tx_hash}")

            # Tunggu konfirmasi
            log.info(f"[{project}] Menunggu konfirmasi transaksi...")
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if receipt.status == 1:
                log.info(f"[{project}] ✅ Mint SUKSES!")
                return True, tx_hash, ""
            else:
                reason = "Transaksi reverted oleh kontrak"
                log.warning(f"[{project}] ❌ {reason}")
                if attempt < MAX_RETRY:
                    await asyncio.sleep(3)
                    continue
                return False, tx_hash, reason

        except Exception as e:
            reason = str(e)
            log.error(f"[{project}] Error attempt {attempt}: {reason}")
            if attempt < MAX_RETRY:
                await asyncio.sleep(5)
            else:
                return False, "", reason

    return False, "", "Max retry tercapai"
