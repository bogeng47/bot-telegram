"""
Template bot airdrop — copy file ini untuk tambah bot baru.

Langkah:
1. Copy file ini → bots/bot_NAMA.py
2. Ganti BOT_NAME, BOT_USERNAME
3. Set IS_WEBAPP = True kalau bot pakai Mini App
4. Daftarkan di bots/__init__.py
"""

from bots.base_bot import BaseBot


class ExampleBot(BaseBot):
    BOT_NAME     = "Nama Bot"
    BOT_USERNAME = "@username_bot"

    # Set True kalau bot pakai Mini App / WebApp (tombol "Buka App")
    # Bot akan otomatis dibuka via Playwright dan tombol Claim/Farm dicari otomatis
    # Set False kalau bot interaksi via chat biasa, lalu override run_task() di bawah
    IS_WEBAPP = True

async def run_task(self) -> tuple[bool, str]:
         try:
            await self.send_command("/start")
            await asyncio.sleep(2)

          messages = await self.client.get_messages(self.BOT_USERNAME, limit=1)
            if not messages:
                return False, "Tidak ada respons dari bot"

            last_msg = messages[0]

           clicked = await self.click_button(last_msg, "Claim")
            if clicked:
                 return True, "Berhasil klik tombol Claim"

             return False, f"Kondisi tidak dikenali: {last_msg.text[:100]}"

       except Exception as e:
            return False, f"Error: {str(e)}"
