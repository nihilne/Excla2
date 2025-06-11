"""
utils/fishing.py
---
Author: Enitoxy
Co-authors: [empty]
License: GPL-3.0
Description: A utility for fishing-related database actions
"""

import random

from data.fish import all_fish
import mongo


class Fish:
    @staticmethod
    async def get_random_fish() -> str:
        while True:
            random_fish = random.choice(list(all_fish))
            fish_chance = all_fish[random_fish]["chance"]
            user_chance = random.uniform(0, 1)

            if user_chance <= fish_chance:
                return random_fish

    @staticmethod
    async def get_fish_emoji(fish: str) -> str | None:
        if fish not in all_fish:
            return None

        emoji_id = all_fish[fish]["emoji_id"]
        if emoji_id:
            return f"<:{fish}:{emoji_id}>"
        else:
            return f":{fish}:"

    @staticmethod
    async def create_inventory(user_id: int) -> None:
        data = {
            "user_id": user_id,
            "bits": 0,
        }
        await mongo.db.inventories.insert_one(data)

    @staticmethod
    async def add_single_fish(user_id: int, fish: str) -> None:
        query = {"user_id": user_id}
        inventory = await mongo.db.inventories.find_one(query)

        if inventory is None:
            await Fish.create_inventory(user_id)

        data = {"$inc": {fish: 1}}
        await mongo.db.inventories.update_one(query, data)
