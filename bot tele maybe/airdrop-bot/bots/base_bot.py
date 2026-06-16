from telethon import TelegramClient


class BaseBot:
    """
    Class dasar untuk semua bot airdrop.
    Setiap bot airdrop baru tinggal extends class ini
    dan override method `run_task`.
    """

    # Nama & username bot — wajib diisi di subclass
    BOT_NAME: str = ""
    BOT_USERNAME: str = ""

    def __init__(self, client: TelegramClient):
        self.client = client

    async def run_task(self) -> tuple[bool, str]:
        """
        Jalanin task utama bot ini.

        Returns:
            (success: bool, note: str)
        """
        raise NotImplementedError("Setiap bot harus implement run_task()")

    async def send_command(self, command: str) -> None:
        """Helper: kirim perintah/pesan ke bot."""
        await self.client.send_message(self.BOT_USERNAME, command)

    async def click_button(self, message, button_text: str) -> bool:
        """
        Helper: klik inline button berdasarkan teks tombol.

        Returns:
            True kalau tombol ditemukan & diklik, False kalau tidak.
        """
        if not message.buttons:
            return False
        for row in message.buttons:
            for button in row:
                if button_text.lower() in button.text.lower():
                    await button.click()
                    return True
        return False
