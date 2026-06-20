import asyncio
import random

import discord
from discord import app_commands
from discord.ext import commands

from core.views.rps import RPSRestartView, RPSView


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def rps_restart(
        self, interaction: discord.Interaction, r_view: RPSRestartView
    ):
        r_view_action = await r_view.wait()  # type: ignore
        if r_view_action is True:  # View timed out
            embed = discord.Embed(
                title="Seems like you didn't make a choice!",
                description="Play again sometime soon!",
                color=0x00BB00,
            )
            await interaction.edit_original_response(embed=embed, view=None)
        else:
            restart = r_view.restart  # type: ignore
            if restart is True:
                await self.rps_game(interaction)
            elif restart is False:
                embed = discord.Embed(
                    title="Thanks for playing!",
                    description="Play again sometime soon!",
                    color=0x00BB00,
                )
                await interaction.edit_original_response(embed=embed, view=None)

    async def rps_game(self, interaction: discord.Interaction):
        rock_emoji = "<:rock:1299423774386425907>"
        paper_emoji = "<:paper:1299426829706203250>"
        scissors_emoji = "<:scissors:1299426819396866159>"
        author = interaction.user.id
        view = RPSView(author)
        embed = discord.Embed(
            title="Make your choice...", description="", color=0x000088
        )
        embed.add_field(name="Your Choice", value="Choosing...")
        embed.add_field(name="Excla!'s Choice", value="Choosing...")
        await interaction.edit_original_response(
            embed=embed, view=view
        )  # Initial Response
        view_action = await view.wait()
        if view_action is True:  # View timed out
            embed = discord.Embed(
                title="Seems like you didn't make a choice!",
                description="Play again sometime soon!",
                color=0x0000BB,
            )
            await interaction.edit_original_response(embed=embed, view=None)
        else:
            user_choice = view.user_choice
            result = None
            choices = ["rock", "paper", "scissors"]
            computer_choice = random.choice(choices)
            if computer_choice == user_choice:
                result = "tie"
            elif computer_choice == "rock" and user_choice == "paper":
                result = "user_win"
            elif computer_choice == "rock" and user_choice == "scissors":
                result = "computer_win"
            elif computer_choice == "paper" and user_choice == "rock":
                result = "computer_win"
            elif computer_choice == "paper" and user_choice == "scissors":
                result = "user_win"
            elif computer_choice == "scissors" and user_choice == "rock":
                result = "user_win"
            elif computer_choice == "scissors" and user_choice == "paper":
                result = "computer_win"

            user_choice = user_choice.capitalize()
            computer_choice = computer_choice.capitalize()

            emj = {"Rock": rock_emoji, "Paper": paper_emoji, "Scissors": scissors_emoji}

            embed = discord.Embed(
                title="And the result is...", description="", color=0x0000BB
            )
            embed.add_field(
                name="Your Choice", value=f"{emj[user_choice]} {user_choice}"
            )
            embed.add_field(name="Excla!'s Choice", value="||Hidden||")
            await interaction.edit_original_response(embed=embed)  # Secondary Response
            await asyncio.sleep(2)

            r_view = RPSRestartView(author)

            if result == "tie":
                embed = discord.Embed(title="Tie!", description="", color=0xFFFF00)
                embed.add_field(
                    name="Your Choice", value=f"{emj[user_choice]} {user_choice}"
                )
                embed.add_field(
                    name="Excla!'s Choice",
                    value=f"{emj[computer_choice]} {computer_choice}",
                )
                await interaction.edit_original_response(embed=embed, view=r_view)
            elif result == "user_win":
                embed = discord.Embed(title="You Win!", description="", color=0x00BB00)
                embed.add_field(
                    name="Your Choice", value=f"{emj[user_choice]} {user_choice}"
                )
                embed.add_field(
                    name="Excla!'s Choice",
                    value=f"{emj[computer_choice]} {computer_choice}",
                )
                await interaction.edit_original_response(embed=embed, view=r_view)
            elif result == "computer_win":
                embed = discord.Embed(
                    title="Excla! Wins!", description="", color=0xBB0000
                )
                embed.add_field(
                    name="Your Choice", value=f"{emj[user_choice]} {user_choice}"
                )
                embed.add_field(
                    name="Excla!'s Choice",
                    value=f"{emj[computer_choice]} {computer_choice}",
                )
                await interaction.edit_original_response(embed=embed, view=r_view)
            else:
                print("You fucked up somewhere")

            await self.rps_restart(interaction, r_view)

    @app_commands.command(
        name="rockpaperscissors", description="Rock Paper Scissors VS Excla!"
    )
    @app_commands.checks.cooldown(1, 5.0)
    async def rps(self, interaction: discord.Interaction):
        """Rock Paper Scissors command"""
        await interaction.response.defer()
        await self.rps_game(interaction)


async def setup(bot):
    await bot.add_cog(Fun(bot))
