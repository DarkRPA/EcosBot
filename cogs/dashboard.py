import discord
from discord.ext import commands
import database


def get_name(guild, user_id):
    member = guild.get_member(user_id)
    return member.display_name if member else f"Usuario {user_id}"


def format_top(guild, data):
    if not data:
        return "Sin datos todavía."

    lines = []

    for index, (user_id, count) in enumerate(data, start=1):
        name = get_name(guild, user_id)
        lines.append(f"**{index}.** {name} — `{count}`")

    return "\n".join(lines)


class DashboardView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=180)
        self.ctx = ctx

    async def update(self, interaction, embed):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "❌ Este dashboard no es tuyo.",
                ephemeral=True
            )
            return

        await interaction.response.edit_message(embed=embed, view=self)

    def general_embed(self):
        stats = database.get_dashboard_stats()

        embed = discord.Embed(
            title="📊 EcosBot Dashboard",
            description="Resumen general del servidor.",
            color=discord.Color.blue()
        )

        embed.add_field(name="👥 Usuarios registrados", value=f"{stats['users_count']:,}", inline=True)
        embed.add_field(name="⚔️ Avalonianas", value=f"{stats['ava_count']:,}", inline=True)
        embed.add_field(name="🧍 Participaciones", value=f"{stats['participations_count']:,}", inline=True)
        embed.add_field(name="💰 Balance total", value=f"{stats['total_balance']:,}", inline=True)
        embed.add_field(name="🪙 Ecoins actuales", value=f"{stats['total_ecoins']:,}", inline=True)
        embed.add_field(name="🪙 Ecoins por Avas", value=f"{stats['ecoins_from_avas']:,}", inline=True)
        embed.add_field(name="⚠️ Warnings", value=f"{stats['warnings_count']:,}", inline=True)
        embed.add_field(name="🛒 Compras tienda", value=f"{stats['shop_purchases']:,}", inline=True)

        return embed

    def avas_embed(self):
        embed = discord.Embed(
            title="⚔️ Dashboard de Avalonianas",
            description="Top jugadores por rol.",
            color=discord.Color.green()
        )

        embed.add_field(
            name="📢 Top Callers",
            value=format_top(self.ctx.guild, database.get_top_by_ava_role("Caller", 5)),
            inline=False
        )

        embed.add_field(
            name="🕵️ Top Scouts",
            value=format_top(self.ctx.guild, database.get_top_by_ava_role("Scout", 5)),
            inline=False
        )

        embed.add_field(
            name="🛡️ Top Party",
            value=format_top(self.ctx.guild, database.get_top_by_ava_role("Party", 5)),
            inline=False
        )

        return embed

    def warnings_embed(self):
        embed = discord.Embed(
            title="⚠️ Dashboard de Warnings",
            description="Usuarios con más warnings.",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="Top Warnings",
            value=format_top(self.ctx.guild, database.get_top_warnings(10)),
            inline=False
        )

        return embed

    def shop_embed(self):
        embed = discord.Embed(
            title="🛒 Dashboard de Tienda",
            description="Usuarios que más han comprado.",
            color=discord.Color.purple()
        )

        embed.add_field(
            name="Top compradores",
            value=format_top(self.ctx.guild, database.get_top_shop_buyers(10)),
            inline=False
        )

        return embed

    @discord.ui.button(label="📊 General", style=discord.ButtonStyle.primary)
    async def general_button(self, interaction, button):
        await self.update(interaction, self.general_embed())

    @discord.ui.button(label="⚔️ Avas", style=discord.ButtonStyle.success)
    async def avas_button(self, interaction, button):
        await self.update(interaction, self.avas_embed())

    @discord.ui.button(label="⚠️ Warnings", style=discord.ButtonStyle.danger)
    async def warnings_button(self, interaction, button):
        await self.update(interaction, self.warnings_embed())

    @discord.ui.button(label="🛒 Tienda", style=discord.ButtonStyle.secondary)
    async def shop_button(self, interaction, button):
        await self.update(interaction, self.shop_embed())


class Dashboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dashboard")
    async def dashboard(self, ctx):
        view = DashboardView(ctx)
        await ctx.send(embed=view.general_embed(), view=view)


async def setup(bot):
    await bot.add_cog(Dashboard(bot))