import asyncio
import random
from dataclasses import dataclass

import discord
from discord import app_commands
from discord.ext import commands

from core.views.rps import EMOJIS, RPSRestartView, RPSView

CHOICES = ["rock", "paper", "scissors"]

OUTCOMES = {
    ("paper", "rock"): "win",
    ("scissors", "paper"): "win",
    ("rock", "scissors"): "win",
}


@dataclass
class RPSSession:
    wins: int = 0
    losses: int = 0
    ties: int = 0

    @property
    def total(self) -> int:
        return self.wins + self.losses + self.ties

    def record(self, result: str):
        if result == "win":
            self.wins += 1
        elif result == "loss":
            self.losses += 1
        elif result == "tie":
            self.ties += 1

    def summary(self) -> str:
        return f"You: {self.wins}, Excla!: {self.losses} ({self.total} Games)"


def get_result(user: str, computer: str) -> str:
    if user == computer:
        return "tie"
    return OUTCOMES.get((user, computer), "loss")


def result_embed(user: str, computer: str) -> tuple[str, str, int]:
    result = get_result(user, computer)
    match result:
        case "win":
            return "win", "You Win!", 0x00BB00
        case "tie":
            return "tie", "Tie!", 0xFFFF00
        case _:
            return "loss", "Excla! Wins!", 0xBB0000


def choices_embed(
    title: str, user: str, computer: str, color: int, session: RPSSession
) -> discord.Embed:
    embed = discord.Embed(title=title, color=color)
    embed.add_field(name="Your Choice", value=f"{EMOJIS[user]} {user.capitalize()}")
    embed.add_field(
        name="Excla!'s Choice", value=f"{EMOJIS[computer]} {computer.capitalize()}"
    )
    embed.set_footer(text=session.summary())
    return embed


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def rps_game(self, interaction: discord.Interaction, session: RPSSession):
        view = RPSView(interaction.user.id)
        embed = discord.Embed(title="Make your choice...", color=0x000088)
        embed.add_field(name="Your Choice", value="Choosing...")
        embed.add_field(name="Excla!'s Choice", value="Choosing...")
        embed.set_footer(text=session.summary())
        await interaction.edit_original_response(embed=embed, view=view)

        timed_out = await view.wait()
        if timed_out:
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="Seems like you didn't make a choice!",
                    description="Play again sometime soon!",
                    color=0x0000BB,
                ),
                view=None,
            )
            return

        user_choice = view.user_choice
        if user_choice is None:
            return

        computer_choice = random.choice(CHOICES)
        result, title, color = result_embed(user_choice, computer_choice)
        session.record(result)

        reveal_embed = discord.Embed(title="And the result is...", color=0x0000BB)
        reveal_embed.add_field(
            name="Your Choice",
            value=f"{EMOJIS[user_choice]} {user_choice.capitalize()}",
        )
        reveal_embed.add_field(name="Excla!'s Choice", value="||Hidden||")
        await interaction.edit_original_response(embed=reveal_embed, view=None)
        await asyncio.sleep(2)

        r_view = RPSRestartView(interaction.user.id)
        await interaction.edit_original_response(
            embed=choices_embed(title, user_choice, computer_choice, color, session),
            view=r_view,
        )

        timed_out = await r_view.wait()
        if timed_out or not r_view.restart:
            end_embed = discord.Embed(
                title="Thanks for playing!",
                description=session.summary(),
                color=0x00BB00,
            )
            await interaction.edit_original_response(embed=end_embed, view=None)
            return

        await self.rps_game(interaction, session)

    @app_commands.command(
        name="rps", description="Rock, paper, scissors against Excla!"
    )
    @app_commands.checks.cooldown(1, 5.0)
    async def rps(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.rps_game(interaction, RPSSession())


async def setup(bot):
    await bot.add_cog(Fun(bot))
