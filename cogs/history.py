import discord
from discord.ext import commands
import database


class History(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="history")
    async def history(self, ctx, member: discord.Member = None, currency: str = None):
        member = member or ctx.author

        if currency:
            currency = currency.lower()

            if currency not in ["balance", "ecoins"]:
                await ctx.send("❌ Usa `balance` o `ecoins`.")
                return

        transactions = database.get_transactions(member.id, currency, 15)

        if not transactions:
            await ctx.send(f"📜 {member.display_name} no tiene historial todavía.")
            return

        lines = [
            f"📜 **Historial de {member.display_name}**",
            ""
        ]

        for amount, curr, reason, created_at in transactions:
            sign = "+" if amount > 0 else ""
            emoji = "💰" if curr == "balance" else "🪙"

            lines.append(
                f"{emoji} `{created_at}` | **{sign}{amount:,} {curr}** | {reason}"
            )

        await ctx.send("\n".join(lines))


async def setup(bot):
    await bot.add_cog(History(bot))