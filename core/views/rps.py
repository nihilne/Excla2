import discord


class RPSView(discord.ui.View):
    """
    Rock Paper Scissors View
    ---
    View Type: `Non-Persistent`
    Timeout (seconds): `60`

    Buttons:
        rock_button: Returns Literal["rock"] (user choice), disables all buttons
        paper_button: Returns Literal["roll_of_paper"] (user choice),
        disables all buttons
        scissors_button: Returns Literal["scissors"] (user choice), disables all buttons
    """

    def __init__(self, author):
        super().__init__(timeout=60)
        self.user_choice: str = None  # type: ignore
        self.author = author

    rock_emoji = "<:bitrock:1350209723072512101>"
    paper_emoji = "<:bitpaper:1350209734673960960>"
    scissors_emoji = "<:bitscissors:1350209748213043342>"

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.author:
            await interaction.response.send_message(
                "This isn't your game! Run /rockpaperscissors to start your game!",
                ephemeral=True,
            )
            return False
        return True

    async def disable_all_buttons(self):
        for child in self.children:
            child.disabled = True  # type: ignore

    @discord.ui.button(
        label="Rock", style=discord.ButtonStyle.blurple, emoji=rock_emoji
    )
    async def rock_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.disable_all_buttons()
        await interaction.response.edit_message(view=self)
        self.user_choice = "rock"
        self.stop()

    @discord.ui.button(
        label="Paper", style=discord.ButtonStyle.blurple, emoji=paper_emoji
    )
    async def paper_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.disable_all_buttons()
        await interaction.response.edit_message(view=self)
        self.user_choice = "paper"
        self.stop()

    @discord.ui.button(
        label="Scissors", style=discord.ButtonStyle.blurple, emoji=scissors_emoji
    )
    async def scissors_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.disable_all_buttons()
        await interaction.response.edit_message(view=self)
        self.user_choice = "scissors"
        self.stop()


class RPSRestartView(discord.ui.View):
    """
    Rock Paper Scissors Restart View
    ---
    View Type: `Non-Persistent`
    Timeout (seconds): `60`
    """

    def __init__(self, author):
        super().__init__(timeout=60)
        self.restart: bool | None = None
        self.author = author

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.author:
            await interaction.response.send_message(
                "This isn't your game! Run /rockpaperscissors to start your game!",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="Play Again", style=discord.ButtonStyle.green)
    async def play_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        await interaction.edit_original_response(view=self)
        self.restart = True
        self.stop()

    @discord.ui.button(label="End Game", style=discord.ButtonStyle.red)
    async def end_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        await interaction.edit_original_response(view=self)
        self.restart = False
        self.stop()
