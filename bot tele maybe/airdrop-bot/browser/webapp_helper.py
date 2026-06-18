"""
Helper untuk:
1. Ambil WebApp URL dari bot Telegram via Telethon
2. Generate initData (Telegram auth) yang valid
3. Buka WebApp di Playwright + inject auth
4. Auto-detect & klik tombol claim/farm
"""

import asyncio
import hashlib
import hmac
import json
import logging
import time
import urllib.parse
from typing import Optional

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from telethon import TelegramClient
from telethon.tl.functions.messages import RequestWebViewRequest
from telethon.tl.types import InputPeerUser

log = logging.getLogger(__name__)

# Kata kunci tombol yang dicari — urutan prioritas
CLAIM_KEYWORDS = [
    "claim", "collect", "farm", "start farming",
    "harvest", "mine", "tap", "check in",
    "daily", "reward", "get reward", "grab",
]

# Kata kunci tombol yang di-skip
SKIP_KEYWORDS = [
    "invite", "referral", "share", "social",
    "task", "leaderboard", "rank", "setting",
    "connect wallet", "buy", "shop",
]


async def get_webapp_url(client: TelegramClient, bot_username: str) -> Optional[str]:
    """
    Ambil WebApp URL dari bot via Telethon.
    Return URL string atau None kalau tidak ketemu.
    """
    try:
        entity = await client.get_entity(bot_username)
        messages = await client.get_messages(bot_username, limit=1)

        if not messages or not messages[0].buttons:
            # Kirim /start dulu kalau tidak ada pesan
            await client.send_message(bot_username, "/start")
            await asyncio.sleep(3)
            messages = await client.get_messages(bot_username, limit=1)

        if not messages or not messages[0].buttons:
            log.warning(f"[{bot_username}] Tidak ada tombol ditemukan")
            return None

        # Cari tombol yang punya WebApp URL
        for row in messages[0].buttons:
            for btn in row:
                if hasattr(btn, "url") and btn.url:
                    if "tgWebApp" in btn.url or "t.me" in btn.url:
                        log.info(f"[{bot_username}] WebApp URL ditemukan via button URL")
                        return btn.url

        # Kalau tidak ada URL di button, coba RequestWebView
        try:
            for row in messages[0].buttons:
                for btn in row:
                    if hasattr(btn.button, "url") and btn.button.url:
                        result = await client(RequestWebViewRequest(
                            peer=await client.get_input_entity(bot_username),
                            bot=await client.get_input_entity(bot_username),
                            platform="android",
                            url=btn.button.url,
                        ))
                        if result and hasattr(result, "url"):
                            log.info(f"[{bot_username}] WebApp URL dari RequestWebView")
                            return result.url
        except Exception as e:
            log.debug(f"[{bot_username}] RequestWebView gagal: {e}")

        return None

    except Exception as e:
        log.error(f"[{bot_username}] Error get_webapp_url: {e}")
        return None


def _find_claim_button(buttons: list) -> Optional[object]:
    """
    Cari tombol claim dari list tombol Playwright.
    Return element tombol atau None.
    """
    candidates = []

    for btn in buttons:
        try:
            text = btn.inner_text().strip().lower()
        except Exception:
            continue

        # Skip tombol yang tidak relevan
        if any(skip in text for skip in SKIP_KEYWORDS):
            continue

        # Skor berdasarkan urutan prioritas keyword
        for i, keyword in enumerate(CLAIM_KEYWORDS):
            if keyword in text:
                candidates.append((i, text, btn))
                break

    if not candidates:
        return None

    # Ambil yang paling prioritas (skor terkecil)
    candidates.sort(key=lambda x: x[0])
    chosen = candidates[0]
    log.info(f"Tombol dipilih: '{chosen[1]}'")
    return chosen[2]


async def run_webapp(
    webapp_url: str,
    bot_name: str,
    headless: bool = True,
    timeout_ms: int = 30000,
) -> tuple[bool, str]:
    """
    Buka WebApp di Playwright, auto-detect & klik tombol claim.

    Returns:
        (success, message)
    """
    async with async_playwright() as p:
        browser: Browser = await p.chromium.launch(
            headless=headless,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-extensions",
            ]
        )

        context: BrowserContext = await browser.new_context(
            viewport={"width": 390, "height": 844},  # ukuran mobile
            user_agent=(
                "Mozilla/5.0 (Linux; Android 13; Pixel 7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/116.0.0.0 Mobile Safari/537.36"
            ),
        )

        page: Page = await context.new_page()

        try:
            log.info(f"[{bot_name}] Membuka WebApp...")
            await page.goto(webapp_url, timeout=timeout_ms, wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle", timeout=timeout_ms)
            await asyncio.sleep(3)  # tunggu animasi/render selesai

            # Cari semua tombol yang visible
            all_buttons = await page.query_selector_all(
                "button:visible, "
                "[role='button']:visible, "
                "a.btn:visible, "
                ".button:visible, "
                "[class*='claim']:visible, "
                "[class*='farm']:visible, "
                "[class*='collect']:visible"
            )

            if not all_buttons:
                # Fallback: ambil semua elemen yang bisa diklik
                all_buttons = await page.query_selector_all(
                    "button, [role='button'], [onclick], .btn"
                )

            log.info(f"[{bot_name}] Ditemukan {len(all_buttons)} tombol")

            # Log semua tombol yang ada untuk debugging
            btn_texts = []
            for btn in all_buttons:
                try:
                    text = await btn.inner_text()
                    if text.strip():
                        btn_texts.append(text.strip())
                except Exception:
                    pass
            log.info(f"[{bot_name}] Tombol tersedia: {btn_texts}")

            # Cari tombol claim
            target_btn = None
            for btn in all_buttons:
                try:
                    text = (await btn.inner_text()).strip().lower()
                except Exception:
                    continue

                if any(skip in text for skip in SKIP_KEYWORDS):
                    continue

                for keyword in CLAIM_KEYWORDS:
                    if keyword in text:
                        target_btn = btn
                        log.info(f"[{bot_name}] Tombol claim ditemukan: '{text}'")
                        break

                if target_btn:
                    break

            if not target_btn:
                return False, f"Tombol claim tidak ditemukan. Tersedia: {btn_texts}"

            # Klik tombol
            await target_btn.scroll_into_view_if_needed()
            await target_btn.click()
            await asyncio.sleep(2)

            # Cek apakah ada popup konfirmasi setelah klik
            confirm_btns = await page.query_selector_all(
                "button:visible, [role='button']:visible"
            )
            for cbtn in confirm_btns:
                try:
                    ctext = (await cbtn.inner_text()).strip().lower()
                    if any(k in ctext for k in ["confirm", "ok", "yes", "submit"]):
                        await cbtn.click()
                        await asyncio.sleep(1)
                        log.info(f"[{bot_name}] Klik konfirmasi: '{ctext}'")
                        break
                except Exception:
                    pass

            return True, f"Berhasil klik tombol claim"

        except Exception as e:
            return False, f"Error Playwright: {str(e)}"

        finally:
            await context.close()
            await browser.close()
