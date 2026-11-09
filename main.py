import asyncio
import logging
import os
from pathlib import Path

from discord import Intents, __version__
from discord.app_commands import AppCommandContext, AppInstallationType
from discord.ext.commands import AutoShardedBot
from dotenv import load_dotenv

from core.utils.logger import setup_custom_logging_format

load_dotenv()

DISCORD_TOKEN = os.environ["TOKEN"]
if not DISCORD_TOKEN:
    raise ValueError("Discord token not found.")

BASE_DIR = Path(__file__).resolve().parent
COGS_DIR = BASE_DIR / "cogs"

log = logging.getLogger("main")


class Bot(AutoShardedBot):
    def __init__(self, command_prefix):
        super().__init__(
            command_prefix=command_prefix,
            intents=Intents.all(),
            allowed_contexts=AppCommandContext(
                guild=True, dm_channel=True, private_channel=True
            ),
            allowed_installs=AppInstallationType(
                guild=True,
                user=True,
            ),
        )

    async def on_ready(self):
        log.info("Excla! is online!")
        log.info(f"Latency: {round(self.latency * 1000, 2)}ms")
        log.info(f"discord.py: {__version__}")
        log.info(f"{len(self.guilds)} servers")

    async def close(self):
        log.info("Shutting down...")
        await super().close()

    async def load_cogs(self, directory: str | Path):
        """Loads cogs from a specific directory"""
        directory = Path(directory)
        package = directory.name

        for cog_file in directory.glob("*.py"):
            if cog_file.stem == "__init__":
                continue
            await self.load_extension(f"{package}.{cog_file.stem}")
            log.info(f"Loaded {cog_file.name}")

    async def setup_hook(self):
        """Loads the cogs and syncs tree"""
        await setup_custom_logging_format()
        await self.load_cogs(COGS_DIR)
        await self.tree.sync()
        log.info("Synced tree")


async def main():
    """Runs the bot"""
    bot = Bot(command_prefix="/")
    async with bot:
        await bot.start(token=DISCORD_TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
