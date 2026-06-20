import discord


EMOJIS = {
    "rock": "<:rock:1350209723072512101>",
    "paper": "<:paper:1350209734673960960>",
    "scissors": "<:scissors:1350209748213043342>",
}


class RPSBaseView(discord.ui.View):
    def __init__(self, author: int):
        super().__init__(timeout=60)
        self.author = author

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author:
            await interaction.response.send_message(
                "This isn't your game! Run /rps to start your own.",
                ephemeral=True,
            )
            return False
        return True


class RPSView(RPSBaseView):
    def __init__(self, author: int):
        super().__init__(author)
        self.user_choice: str | None = None

    async def _pick(self, interaction: discord.Interaction, choice: str):
        for child in self.children:
            child.disabled = True  # type: ignore
        await interaction.response.edit_message(view=self)
        self.user_choice = choice
        self.stop()

    @discord.ui.button(
        label="Rock", style=discord.ButtonStyle.blurple, emoji=EMOJIS["rock"]
    )
    async def rock_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self._pick(interaction, "rock")

    @discord.ui.button(
        label="Paper", style=discord.ButtonStyle.blurple, emoji=EMOJIS["paper"]
    )
    async def paper_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self._pick(interaction, "paper")

    @discord.ui.button(
        label="Scissors", style=discord.ButtonStyle.blurple, emoji=EMOJIS["scissors"]
    )
    async def scissors_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self._pick(interaction, "scissors")


class RPSRestartView(RPSBaseView):
    def __init__(self, author: int):
        super().__init__(author)
        self.restart: bool | None = None

    @discord.ui.button(label="Play Again", style=discord.ButtonStyle.green)
    async def play_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        self.restart = True
        self.stop()

    @discord.ui.button(label="End Game", style=discord.ButtonStyle.red)
    async def end_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        self.restart = False
        self.stop()
