"""
cogs.economy.py
---
Author: Enitoxy
Co-authors: [empty]
License: GPL-3.0
Description: A cog/module containing economy commands (fishing)
"""

import logging

from discord import Embed, Interaction, app_commands
from discord.app_commands import Choice
from discord.ext import commands

from utils import logger, mongo

log = logging.getLogger(__name__)


class Economy(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    # Most of the commands without `@app_commands.command` are database-related functions
    async def get_fish(self):
        while True:
            random_fish = random.choice(list(fishes))
            fish_chance = fishes[random_fish]["chance"]
            user_chance = random.uniform(0, 1)

            if user_chance <= fish_chance:
                return random_fish

    async def get_emoji(self, fish: str):
        if fish not in fishes:
            return None

        emoji_id = fishes[fish]["emoji_id"]
        if emoji_id is None:
            return f":{fish}:"
        else:
            return f"<:{fish}:{emoji_id}>"

    async def new_inventory(self, user_id: int):
        data = {
            "user_id": user_id,
            "bits": 0,
        }
        return await db.inventory.insert_one(data)

    async def add_one_fish(self, user_id: int, fish: str):
        query = {"user_id": user_id}
        user_inventory = await db.inventory.find_one(query)

        if user_inventory is None:
            await self.new_inventory(user_id)

        data = {"$inc": {fish: 1}}
        return await db.inventory.update_one(query, data)

    async def sell_amount(self, user_id: int, item: str, amount: int):
        query = {"user_id": user_id}
        _filter = {item: 1}
        user_inventory = await db.inventory.find_one(query, _filter)

        if user_inventory[item] <= 0 or item not in user_inventory:
            return {
                "status": False,
                "message": "Hmm... it seems like you don't have that item!",
            }

        if user_inventory[item] < amount:
            return {
                "status": False,
                "message": "Hmm... it seems like you don't have enough of that item!",
            }

        if amount <= 0:
            return {
                "status": False,
                "message": "You sold... nothing.",
            }

        item_value = fishes[item]["value"]
        sale_value = item_value * amount
        update = {
            "$inc": {
                "bits": sale_value,
                item: -amount,
            }
        }
        await db.inventory.update_one(query, update)
        return {
            "status": True,
            "value": sale_value,
            "amount": amount,
        }

    async def sell_all(self, user_id: int, item: str):
        query = {"user_id": user_id}
        _filter = {item: 1}
        user_inventory = await db.inventory.find_one(query, _filter)

        if item not in user_inventory:
            return {
                "status": False,
                "message": "Hmm... it seems like you don't have that item!",
            }

        item_amount = user_inventory[item]

        if item_amount <= 0:
            return {
                "status": False,
                "message": "Hmm... it seems like you don't have that item!",
            }

        item_value = fishes[item]["value"]
        sale_value = item_value * item_amount
        update = {
            "$inc": {
                "bits": sale_value,
                item: -item_amount,
            }
        }
        await db.inventory.update_one(query, update)
        return {
            "status": True,
            "value": sale_value,
            "amount": item_amount,
        }

    @app_commands.command(name="fish")
    async def fish(self, interaction: Interaction):
        fish = await self.get_fish()
        fish_name = fishes[fish]["name"]
        fish_value = fishes[fish]["value"]

        await self.add_one_fish(interaction.user.id, fish)

        emoji = await self.get_emoji(fish)

        embed = Embed(title="Fishin' time!", description="")
        embed.add_field(name="You caught:", value=fish_name)
        embed.add_field(name=emoji, value="")
        embed.add_field(name=f"Value: {fish_value}", value="", inline=False)

        return await interaction.response.send_message(embed=embed)

    @app_commands.command(name="inventory")
    async def inventory(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        # This time, we'll use a filter because we only want to know about the items.
        query = {"user_id": interaction.user.id}
        _filter = {"_id": 0, "user_id": 0, "bits": 0}
        user_inventory = await db.inventory.find_one(query, _filter)

        if user_inventory is None:
            embed = Embed(
                title="You don't have anything in your inventory!",
                description="Try catching something with `/fish`!",
            )
            return await interaction.followup.send(embed=embed)

        embed = Embed(title="Your Inventory", description="")

        inventory_value = 0
        for item in user_inventory:
            if user_inventory[item] == 0:
                continue
            fish_name = fishes[item]["name"]
            fish_value = fishes[item]["value"]
            fish_amount = user_inventory[item]
            fish_emoji = await self.get_emoji(item)

            inventory_value += fish_amount * fish_value

            embed.add_field(
                name=f"{fish_amount} {fish_name} {fish_emoji} x {fish_value}",
                value=f"Total: {fish_amount * fish_value}",
                inline=False,
            )

        embed.set_footer(text=f"Total inventory value: {inventory_value}")
        return await interaction.followup.send(embed=embed)

    @app_commands.command(name="balance")
    async def balance(self, interaction: Interaction):
        query = {"user_id": interaction.user.id}
        _filter = {"_id": 0, "bits": 1}
        user_inventory = await db.inventory.find_one(query, _filter)

        if user_inventory is None:
            embed = Embed(
                title="You don't have a balance yet!",
                description="Try selling some fish with `/sell`!",
            )
            return await interaction.response.send_message(embed=embed)

        embed = Embed(
            title="Your Balance",
            description=f"{user_inventory['bits']} bits",
        )
        return await interaction.response.send_message(embed=embed)

    @app_commands.command(name="sell")
    async def sell(
        self,
        interaction: Interaction,
        action: str,
        item: str,
        amount: int = 1,
    ):
        if item not in fishes:
            return await interaction.response.send_message(
                "Hmm... it seems like this item doesn't exist. Please try one of the shown options when running the command."
            )

        if action == "sell_all":
            sale = await self.sell_all(interaction.user.id, item)
        elif action == "sell_amount":
            sale = await self.sell_amount(interaction.user.id, item, amount)
        else:
            return await interaction.response.send_message(
                "Hmm... it seems like this action doesn't exist. Please try one of the shown options when running the command."
            )

        if not sale["status"]:
            return await interaction.response.send_message(sale["message"])

        item_name = fishes[item]["name"]
        item_emoji = await self.get_emoji(item)
        embed = Embed(title="Sold!", description="")
        embed.add_field(
            name=f"{sale['amount']} x {item_emoji} {item_name}",
            value=f"Sold for {sale['value']} bits",
            inline=False,
        )

        return await interaction.response.send_message(embed=embed)

    @sell.autocomplete("action")
    async def sell_autocomplete_action(
        self,
        interaction: Interaction,
        current: str,
    ):
        choices = [
            Choice(name="Sell everything", value="sell_all"),
            Choice(name="Sell specific amount", value="sell_amount"),
        ]
        return choices

    @sell.autocomplete("item")
    async def sell_autocomplete_item(self, interaction: Interaction, current: str):
        items = []
        query = {"user_id": interaction.user.id}
        _filter = {"_id": 0, "user_id": 0, "bits": 0}

        if current:
            for fish in fishes:
                if fishes[fish]["name"].lower().startswith(current.lower()):
                    _filter = {"_id": 0}
                    _filter[fish] = 1

        user_inventory = await db.inventory.find_one(query, _filter)

        if user_inventory is None:
            return []

        for item in user_inventory:
            if user_inventory[item] > 0:
                item_name = fishes[item]["name"]
                items.append(Choice(name=item_name, value=item))

        return items


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Economy(bot))
