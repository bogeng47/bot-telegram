"""
Template bot airdrop — copy file ini untuk tambah bot baru.
Ganti BOT_NAME, BOT_USERNAME, dan isi logika di run_task().
"""

import asyncio
from bots.base_bot import BaseBot


class ExampleBot(BaseBot):
    BOT_NAME = "Example Airdrop"
    BOT_USERNAME = "@contoh_airdrop_bot"  # ganti dengan username bot target

    async def run_task(self) -> tuple[bool, str]:
        try:
            # 1. Kirim perintah start ke bot
            await self.send_command("/start")
            await asyncio.sleep(2)

            # 2. Ambil pesan terakhir dari bot
            messages = await self.client.get_messages(self.BOT_USERNAME, limit=1)
            if not messages:
                return False, "Tidak ada respons dari bot"

            last_msg = messages[0]

            # 3. Klik tombol kalau ada
            clicked = await self.click_button(last_msg, "Claim")
            if clicked:
                await asyncio.sleep(2)
                return True, "Berhasil klik tombol Claim"

            # 4. Atau cek teks respons
            if "reward" in last_msg.text.lower():
                return True, "Reward sudah tersedia"

            return False, f"Kondisi tidak dikenali: {last_msg.text[:100]}"

        except Exception as e:
            return False, f"Error: {str(e)}"
