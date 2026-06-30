import discord
from discord.ext import commands
import database


PAGE_SIZE = 10


def get_member_name(ctx, user_id):
    member = ctx.guild.get_member(user_id)
    return member.display_name if member else f"Usuario {user_id}"


def get_medal(index):
    return {1: "🥇", 2: "🥈", 3: "🥉", 10: "🔟"}.get(index, f"{index}.")


class LeaderboardView(discord.ui.View):
    def __init__(self, ctx, users, title, value_index):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.users = users
        self.title = title
        self.value_index = value_index
        self.page = 0

    def build_text(self):
        total_pages = max(1, (len(self.users) + PAGE_SIZE - 1) // PAGE_SIZE)
        start = self.page * PAGE_SIZE
        end = start + PAGE_SIZE
        page_users = self.users[start:end]

        lines = [
            self.title,
            f"Página **{self.page + 1}/{total_pages}**",
            ""
        ]

        for i, user_data in enumerate(page_users, start=start + 1):
            user_id = user_data[0]
            value = user_data[self.value_index]
            name = get_member_name(self.ctx, user_id)
            medal = get_medal(i)

            lines.append(f"{medal} **{name}** — {value:,}")

        return "\n".join(lines)

    async def update_message(self, interaction):
        await interaction.response.edit_message(
            content=self.build_text(),
            view=self
        )

    @discord.ui.button(label="⬅️ Anterior", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Este ranking no es tuyo.", ephemeral=True)
            return

        if self.page > 0:
            self.page -= 1

        await self.update_message(interaction)

    @discord.ui.button(label="➡️ Siguiente", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Este ranking no es tuyo.", ephemeral=True)
            return

        total_pages = max(1, (len(self.users) + PAGE_SIZE - 1) // PAGE_SIZE)

        if self.page < total_pages - 1:
            self.page += 1

        await self.update_message(interaction)


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="topbal")
    async def topbal(self, ctx):
        users = database.get_all_users()
        users = sorted(users, key=lambda x: x[1], reverse=True)

        if not users:
            await ctx.send("No hay usuarios registrados.")
            return

        view = LeaderboardView(
            ctx,
            users,
            "🏆 **BALANCE RANKING**",
            1
        )

        await ctx.send(view.build_text(), view=view)

    @commands.command(name="topecoins")
    async def topecoins(self, ctx):
        users = database.get_all_users()
        users = sorted(users, key=lambda x: x[2], reverse=True)

        if not users:
            await ctx.send("No hay usuarios registrados.")
            return

        view = LeaderboardView(
            ctx,
            users,
            "🪙 **ECOINS RANKING**",
            2
        )

        await ctx.send(view.build_text(), view=view)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))