import discord
from discord.ext import commands
from datetime import timedelta
import database


class Ecoins(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addecoins(self, ctx, member: discord.Member, amount: int):
        database.add_ecoins(member.id, amount)
        await ctx.send(f"🪙 Sumados {amount} Ecoins a {member.mention}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removeecoins(self, ctx, member: discord.Member, amount: int):
        database.add_ecoins(member.id, -amount)
        await ctx.send(f"🪙 Restados {amount} Ecoins a {member.mention}")

    @commands.command()
    async def buymute(self, ctx, member: discord.Member):
        cost = 50

        if member == ctx.author:
            await ctx.send("❌ No puedes mutearte a ti mismo.")
            return

        if member.bot:
            await ctx.send("❌ No puedes mutear bots.")
            return

        balance, ecoins = database.get_user(ctx.author.id)

        if ecoins < cost:
            await ctx.send(f"❌ No tienes suficientes Ecoins. Necesitas {cost}.")
            return

        database.add_ecoins(ctx.author.id, -cost)

        await member.timeout(
            discord.utils.utcnow() + timedelta(minutes=1),
            reason=f"Mute comprado por {ctx.author}"
        )

        await ctx.send(
            f"🔇 {ctx.author.mention} ha gastado **{cost} Ecoins** "
            f"para mutear a {member.mention} durante **1 minuto**."
        )


async def setup(bot):
    await bot.add_cog(Ecoins(bot))