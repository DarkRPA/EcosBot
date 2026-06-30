import aiohttp
import discord
from discord.ext import commands
import config
import database
from utils.logger import send_log


async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=15) as response:
            if response.status != 200:
                return None
            return await response.json()


def get_nested(data, path, default=0):
    current = data

    for key in path:
        if not isinstance(current, dict):
            return default

        current = current.get(key)

        if current is None:
            return default

    return current


def parse_fame(data):
    lifetime = data.get("LifetimeStatistics", {})

    pve = get_nested(lifetime, ["PvE", "Total"], 0)

    gathering = get_nested(lifetime, ["Gathering", "All", "Total"], 0)

    crafting = get_nested(lifetime, ["Crafting", "Total"], 0)

    kill = data.get("KillFame", 0)

    return pve, gathering, crafting, kill


class FameTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def snapshot_user(self, ava_message_id, discord_id, snapshot_type):
        player = database.get_registered_player(discord_id)

        if not player:
            return None

        _, albion_id, albion_name, *_ = player

        url = f"{config.ALBION_API_BASE}/players/{albion_id}"
        data = await fetch_json(url)

        if data is None:
            return None

        pve, gathering, crafting, kill = parse_fame(data)

        database.add_fame_snapshot(
            ava_message_id,
            discord_id,
            snapshot_type,
            pve,
            gathering,
            crafting,
            kill
        )

        return {
            "albion_name": albion_name,
            "pve": pve,
            "gathering": gathering,
            "crafting": crafting,
            "kill": kill
        }

    async def snapshot_all_registered_start(self, ava_message_id):
        players = database.get_registered_players()

        for discord_id, *_ in players:
            await self.snapshot_user(ava_message_id, discord_id, "start")

    async def process_ava_fame_end(self, guild, ava_message_id, user_ids):
        lines = []

        for user_id in user_ids:
            start = database.get_start_fame_snapshot(ava_message_id, user_id)

            if not start:
                continue

            end = await self.snapshot_user(ava_message_id, user_id, "end")

            if not end:
                continue

            start_pve, start_gathering, start_crafting, start_kill = start

            gained_pve = end["pve"] - start_pve
            gained_gathering = end["gathering"] - start_gathering
            gained_crafting = end["crafting"] - start_crafting
            gained_kill = end["kill"] - start_kill
            database.add_ava_fame_result(
                ava_message_id,
                user_id,
                gained_pve,
                gained_gathering,
                gained_crafting,
                gained_kill
            )

            member = guild.get_member(user_id)
            name = member.display_name if member else end["albion_name"]

            lines.append(
                f"**{name}**\n"
                f"PvE: +{gained_pve:,}\n"
                f"Gathering: +{gained_gathering:,}\n"
                f"Crafting: +{gained_crafting:,}\n"
                f"Kill Fame: +{gained_kill:,}"
            )

        if not lines:
            return

        await send_log(
            self.bot,
            "📈 Fame ganada en Avaloniana",
            "\n\n".join(lines[:15]),
            discord.Color.green()
        )


async def setup(bot):
    await bot.add_cog(FameTracker(bot))