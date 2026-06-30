import discord
from discord.ext import commands
import database
from utils.logger import send_log


ACHIEVEMENTS = [
    {
        "key": "avas_10",
        "name": "10 Avalonianas",
        "role": "🏅 Ava Novice",
        "type": "total_avas",
        "required": 10
    },
    {
        "key": "avas_50",
        "name": "50 Avalonianas",
        "role": "⚔️ Ava Veteran",
        "type": "total_avas",
        "required": 50
    },
    {
        "key": "avas_100",
        "name": "100 Avalonianas",
        "role": "👑 Ava Legend",
        "type": "total_avas",
        "required": 100
    },
    {
        "key": "caller_20",
        "name": "20 Callers",
        "role": "📢 Caller Veteran",
        "type": "caller_count",
        "required": 20
    },
    {
        "key": "scout_20",
        "name": "20 Scouts",
        "role": "🕵️ Scout Veteran",
        "type": "scout_count",
        "required": 20
    },
]


async def get_or_create_role(guild, role_name):
    role = discord.utils.get(guild.roles, name=role_name)

    if role is None:
        role = await guild.create_role(name=role_name)

    return role


class Achievements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check_user_achievements(self, guild, user_id):
        member = guild.get_member(user_id)

        if member is None:
            return

        stats = database.get_user_ava_stats(user_id)

        total_avas = stats[0] or 0
        caller_count = stats[1] or 0
        scout_count = stats[2] or 0
        party_count = stats[3] or 0

        values = {
            "total_avas": total_avas,
            "caller_count": caller_count,
            "scout_count": scout_count,
            "party_count": party_count
        }

        for achievement in ACHIEVEMENTS:
            current_value = values[achievement["type"]]

            if current_value < achievement["required"]:
                continue

            if database.has_achievement(user_id, achievement["key"]):
                continue

            role = await get_or_create_role(guild, achievement["role"])
            await member.add_roles(role)

            database.add_achievement(user_id, achievement["key"])

            await send_log(
                self.bot,
                "🏆 Logro desbloqueado",
                f"Usuario: {member.mention}\n"
                f"Logro: **{achievement['name']}**\n"
                f"Rol otorgado: **{achievement['role']}**",
                discord.Color.gold()
            )

    @commands.command(name="achievements")
    async def achievements(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        stats = database.get_user_ava_stats(member.id)

        total_avas = stats[0] or 0
        caller_count = stats[1] or 0
        scout_count = stats[2] or 0
        party_count = stats[3] or 0

        lines = [
            f"🏆 **Logros de {member.display_name}**",
            "",
            f"⚔️ Avalonianas: **{total_avas}**",
            f"📢 Caller: **{caller_count}**",
            f"🕵️ Scout: **{scout_count}**",
            f"🛡️ Party: **{party_count}**",
            ""
        ]

        for achievement in ACHIEVEMENTS:
            value = {
                "total_avas": total_avas,
                "caller_count": caller_count,
                "scout_count": scout_count,
                "party_count": party_count
            }[achievement["type"]]

            status = "✅" if value >= achievement["required"] else "❌"

            lines.append(
                f"{status} **{achievement['name']}** "
                f"({value}/{achievement['required']})"
            )

        await ctx.send("\n".join(lines))


async def setup(bot):
    await bot.add_cog(Achievements(bot))