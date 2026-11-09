import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from app import server
from core.utils import logger

load_dotenv()

DISCORD_TOKEN = os.environ["TOKEN"]
if not DISCORD_TOKEN:
    raise ValueError("Discord token not found.")

INTENTS = discord.Intents.all()
COMMAND_PREFIX = "/"

log = logging.getLogger("main")


class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=COMMAND_PREFIX, intents=INTENTS)

    async def on_ready(self):
        log.info("Excla! is online!")
        log.info(f"Latency: {round(self.latency, 4)}ms")
        log.info(f"Discord.py: {discord.__version__}")
        log.info(f"{len(self.guilds)} servers")

    async def close(self):
        log.info("Shutting down...")

    async def load_cogs(self):
        """Loads cogs from a specific directory"""
        for cog_file in os.listdir("./cogs"):
            if cog_file.endswith("indev"):
                pass

            if cog_file.endswith(".py"):
                await self.load_extension(f"cogs.{cog_file[:-3]}")
                log.info(f"Loaded {cog_file}")

    async def setup_hook(self):
        """Starts tasks, loads cogs, syncs tree"""
        await logger.setup_custom_format()
        await self.load_cogs()
        await self.tree.sync()
        log.info("Synced tree")


async def main():
    """Runs the bot and website"""
    bot = Bot()
    async with bot:
        bot_task = asyncio.create_task(bot.start(token=DISCORD_TOKEN))
        app_task = asyncio.create_task(server.serve())
        await asyncio.gather(bot_task, app_task)


if __name__ == "__main__":
    asyncio.run(main())
