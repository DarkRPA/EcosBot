import discord
from discord.ext import commands
import database


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stats")
    async def stats(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        balance, ecoins = database.get_user(member.id)
        ava_stats = database.get_user_ava_stats(member.id)
        history = database.get_user_ava_history(member.id, 10)

        total_avas = ava_stats[0] or 0
        caller_count = ava_stats[1] or 0
        scout_count = ava_stats[2] or 0
        party_count = ava_stats[3] or 0
        ecoins_from_avas = ava_stats[4] or 0

        lines = [
            f"📊 **Stats de {member.display_name}**",
            "",
            f"💰 Balance: **{balance:,}**",
            f"🪙 Ecoins: **{ecoins:,}**",
            "",
            f"⚔️ Avalonianas: **{total_avas}**",
            f"📢 Caller: **{caller_count}**",
            f"🕵️ Scout: **{scout_count}**",
            f"🛡️ Party: **{party_count}**",
            f"🪙 Ecoins por Avas: **{ecoins_from_avas}**",
            "",
            "📜 **Últimas Avas:**"
        ]

        if not history:
            lines.append("No hay historial todavía.")
        else:
            for role, ecoins_given, created_at in history:
                lines.append(f"- {created_at} | {role} | +{ecoins_given} Ecoins")

        await ctx.send("\n".join(lines))


async def setup(bot):
    await bot.add_cog(Stats(bot))