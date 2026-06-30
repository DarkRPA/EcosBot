import discord
from discord.ext import commands
import database


def get_name(guild, user_id):
    member = guild.get_member(user_id)
    return member.display_name if member else f"Usuario {user_id}"


class AvaFameStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="avafame")
    async def avafame(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        stats = database.get_user_ava_fame_stats(member.id)
        history = database.get_user_ava_fame_history(member.id, 5)

        avas = stats[0] or 0
        total_pve = stats[1] or 0
        total_gathering = stats[2] or 0
        total_crafting = stats[3] or 0
        total_kill = stats[4] or 0
        best_pve = stats[5] or 0
        avg_pve = int(stats[6] or 0)

        if avas == 0:
            await ctx.send(f"📈 {member.display_name} todavía no tiene fame registrada en Avas.")
            return

        embed = discord.Embed(
            title=f"📈 Fame de Avalonianas — {member.display_name}",
            description="Solo cuenta la fama registrada durante Avalonianas.",
            color=discord.Color.green()
        )

        embed.add_field(name="⚔️ Avas registradas", value=f"{avas:,}", inline=True)
        embed.add_field(name="📊 PvE total", value=f"{total_pve:,}", inline=True)
        embed.add_field(name="📈 Media PvE/Ava", value=f"{avg_pve:,}", inline=True)
        embed.add_field(name="🏆 Mejor Ava PvE", value=f"{best_pve:,}", inline=True)
        embed.add_field(name="🗡️ Kill Fame", value=f"{total_kill:,}", inline=True)
        embed.add_field(name="🌳 Gathering", value=f"{total_gathering:,}", inline=True)

        lines = []

        for ava_message_id, pve, gathering, crafting, kill, created_at in history:
            lines.append(
                f"`{created_at}` | PvE **+{pve:,}** | Kill **+{kill:,}**"
            )

        embed.add_field(
            name="📜 Últimas Avas",
            value="\n".join(lines) if lines else "Sin historial.",
            inline=False
        )

        await ctx.send(embed=embed)

    @commands.command(name="avafametop")
    async def avafametop(self, ctx):
        data = database.get_top_ava_fame(10)

        if not data:
            await ctx.send("📈 Todavía no hay datos de fame de Avas.")
            return

        lines = ["🏆 **Top Fame PvE en Avalonianas**", ""]

        for index, (user_id, total_pve) in enumerate(data, start=1):
            name = get_name(ctx.guild, user_id)
            lines.append(f"**{index}.** {name} — **{total_pve:,}**")

        await ctx.send("\n".join(lines))

    @commands.command(name="lastavafame")
    async def lastavafame(self, ctx):
        data = database.get_last_ava_fame_results()

        if not data:
            await ctx.send("📈 Todavía no hay resultados de la última Ava.")
            return

        lines = ["📈 **Fame de la última Avaloniana**", ""]

        for index, (user_id, pve, gathering, crafting, kill) in enumerate(data[:15], start=1):
            name = get_name(ctx.guild, user_id)
            lines.append(
                f"**{index}.** {name} — PvE **+{pve:,}** | Kill **+{kill:,}**"
            )

        await ctx.send("\n".join(lines))

    @commands.command(name="guildavafame")
    async def guildavafame(self, ctx):
        data = database.get_guild_ava_fame_stats()

        if not data:
            await ctx.send("🏰 Todavía no hay datos de fame por gremio.")
            return

        lines = ["🏰 **Fame PvE por gremio en Avalonianas**", ""]

        for guild_name, users_count, total_pve in data[:15]:
            guild_name = guild_name or "Sin gremio"
            avg = int(total_pve / users_count) if users_count else 0

            lines.append(
                f"**{guild_name}** — {total_pve:,} PvE | {users_count} jugadores | media {avg:,}"
            )

        await ctx.send("\n".join(lines))


async def setup(bot):
    await bot.add_cog(AvaFameStats(bot))