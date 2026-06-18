from telethon import TelegramClient


class BaseBot:
    """
    Class dasar untuk semua bot airdrop.
    Setiap bot airdrop baru tinggal extends class ini
    dan override method `run_task`.

    - Bot chat biasa: override run_task() dan gunakan send_command/click_button
    - Bot WebApp    : set IS_WEBAPP = True, override get_webapp_url() kalau perlu
    """

    BOT_NAME: str     = ""
    BOT_USERNAME: str = ""

    # Set True kalau bot ini pakai Mini App / WebApp
    IS_WEBAPP: bool = False

    def __init__(self, client: TelegramClient):
        self.client = client

    async def run_task(self) -> tuple[bool, str]:
        """
        Jalanin task utama.
        Kalau IS_WEBAPP=True, otomatis pakai Playwright.
        Kalau IS_WEBAPP=False, override method ini di subclass.
        """
        if self.IS_WEBAPP:
            return await self._run_webapp_task()
        raise NotImplementedError("Override run_task() atau set IS_WEBAPP=True")

    async def _run_webapp_task(self) -> tuple[bool, str]:
        """Internal: jalanin task via Playwright untuk WebApp bot."""
        from browser.webapp_helper import get_webapp_url, run_webapp

        url = await get_webapp_url(self.client, self.BOT_USERNAME)
        if not url:
            return False, "Gagal mendapatkan WebApp URL"

        return await run_webapp(url, self.BOT_NAME)

    async def send_command(self, command: str) -> None:
        """Helper: kirim perintah/pesan ke bot."""
        await self.client.send_message(self.BOT_USERNAME, command)

    async def click_button(self, message, button_text: str) -> bool:
        """
        Helper: klik inline button berdasarkan teks tombol.
        Return True kalau tombol ditemukan & diklik.
        """
        if not message.buttons:
            return False
        for row in message.buttons:
            for button in row:
                if button_text.lower() in button.text.lower():
                    await button.click()
                    return True
        return False
