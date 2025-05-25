"""
cogs.welcome.py
---
Author: Enitoxy
Co-authors: [empty]
License: GPL-3.0
Description: A cog/module containing functionality for welcoming new server members
"""

import discord
from discord import Embed, Interaction, Member
from discord.app_commands import Choice, Group
from discord.ext import commands

from utils import db


class Welcome(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        guild_id = member.guild.id
        query = {"guild_id": guild_id}
        guild_entry = await db.welcome_channels.find_one(query)

        if guild_entry is None:
            return

        channel_id = guild_entry["channel_id"]
        channel = self.bot.get_channel(channel_id)

        embed = Embed(
            title="Welcome!",
            description=f"{member.mention} has joined the server!",
        )
        embed.set_thumbnail(url=member.avatar)
        await channel.send(embed=embed)

    welcome = Group(name="welcome", description="Welcome commands")

    async def add_channel(self, guild_id: int, channel_id: int):
        query = {"guild_id": guild_id}
        guild_entry = await db.welcome_channels.find_one(query)

        if guild_entry is None:
            new_guild = {
                "guild_id": guild_id,
                "channel_id": channel_id,
            }
            await db.welcome_channels.insert_one(new_guild)
            return {"result": f"Set up <#{channel_id}> as a **new** welcome channel!"}

        current_channel = guild_entry["channel_id"]
        if current_channel != channel_id:
            new_channel = {"channel_id": channel_id}
            await db.welcome_channels.update_one(query, new_channel)
            return {
                "result": f"Updated from <#{current_channel}> channel to <#{channel_id}> channel!"
            }

        return {"result": f"Channel <#{current_channel}> is already set up!"}

    async def remove_channel(self, guild_id: int):
        query = {"guild_id": guild_id}
        guild_entry = await db.welcome_channels.find_one(query)

        if guild_entry is None:
            return {"result": "No welcome channels were found for this guild!"}

        await db.welcome_channels.delete_one(query)
        return {"result": "Welcome channel configuration removed!"}

    @welcome.command(name="add")
    async def welcome_add(self, interaction: Interaction, channel: str):
        welcome_channel = await self.bot.fetch_channel(int(channel))

        if welcome_channel not in interaction.guild.channels:
            return await interaction.response.send_message(
                "Hmm... it seems like that channel is not from your server!"
            )

        setup = await self.add_channel(welcome_channel.guild.id, welcome_channel.id)

        return await interaction.response.send_message(setup["result"])

    @welcome_add.autocomplete("channel")
    async def welcome_add_autocomplete(self, interaction: Interaction, current: str):
        if interaction.guild is None:
            return

        channels = []
        if len(channels) < 25:
            for channel in interaction.guild.text_channels:
                channels.append(Choice(name=channel.name, value=str(channel.id)))

        return channels

    @welcome_add.error
    async def welcome_add_error(self, interaction: Interaction, error):
        if isinstance(error, discord.InvalidData):
            return await interaction.response.send_message(
                "Something went wrong... please try again later!"
            )

        if isinstance(error, discord.HTTPException):
            return await interaction.response.send_message(
                "Something went wrong while searching for the channel... please try again later!"
            )

        if isinstance(error, discord.NotFound):
            return await interaction.response.send_message(
                "Hmm... this channel doesn't seem to exist!"
            )

        if isinstance(error, discord.Forbidden):
            return await interaction.response.send_message(
                "Hmm... it seems like Excla! can't fetch this channel... Try checking if Excla! has the proper permissions"
            )

    @welcome.command(name="remove")
    async def welcome_remove(self, interaction: Interaction):
        remove = await self.remove_channel(interaction.guild.id)
        return await interaction.response.send_message(remove["result"])


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Welcome(bot))
