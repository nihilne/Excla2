"""
cogs.web.py
---
Author: Enitoxy
Co-authors: [empty]
License: GPL-3.0
Description: A cog/module containing several fun APIs
"""

from aiohttp import ClientSession
from discord import Embed, Interaction, app_commands
from discord.ext import commands


class Web(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(name="xkcd", description="Daily xkcd")
    @app_commands.checks.cooldown(1, 5.0)
    async def xkcd(self, interaction: Interaction):
        """XKCD command"""
        await interaction.response.defer(thinking=True)

        url = "https://xkcd.com/info.0.json"

        async with ClientSession() as session:
            async with session.get(url) as request:
                response = await request.json()

        embed = Embed(
            title=response["safe_title"],
            description=response["alt"],
        )
        embed.set_image(url=response["img"])
        embed.set_footer(text="By xkcd")
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Web(bot))
