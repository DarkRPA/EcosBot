import discord
from discord.ext import commands
import database


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="profile")
    async def profile(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        balance, ecoins = database.get_user(member.id)
        warnings = database.get_warnings(member.id)
        warning_count = len(warnings)
        total_fines = sum(row[2] for row in warnings)

        await ctx.send(
            f"📋 **Perfil de {member.display_name}**\n\n"
            f"💰 Balance: **{balance:,}**\n"
            f"🪙 Ecoins: **{ecoins:,}**\n"
            f"⚠️ Warnings: **{warning_count}**\n"
            f"💸 Multas totales: **{total_fines:,}**"
        )


async def setup(bot):
    await bot.add_cog(Profile(bot))