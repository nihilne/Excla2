import random

import discord
from discord.ext import commands, tasks


class Status(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    async def cog_load(self):
        self.status_task.start()

    async def cog_unload(self):
        self.status_task.cancel()

    @tasks.loop(minutes=2)
    async def status_task(self):
        """Changes the bot's status message every 2 minutes"""
        n = len(self.bot.guilds)
        status_list = [
            "beep boop",
            "boop beep boop?",
            f"In {n} {'servers' if n != 1 else 'server'}.",
        ]
        activity = discord.CustomActivity(name=random.choice(status_list))
        await self.bot.change_presence(activity=activity)

    @status_task.before_loop
    async def before_status_task(self):
        """Wait before starting the status task loop"""
        await self.bot.wait_until_ready()


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Status(bot))
