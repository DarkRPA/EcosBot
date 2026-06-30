import discord
from discord.ext import commands
import database
import config
from utils.logger import send_log


def get_warning_type(text):
    text = text.lower()

    for warning_name, data in config.WARNING_TYPES.items():
        for alias in data["aliases"]:
            if alias in text:
                return warning_name

    return None


def calculate_fine(user_id, warning_type):
    data = config.WARNING_TYPES[warning_type]

    if data.get("escalate"):
        current_warnings = database.get_warning_count(user_id)
        fines = data["fines"]
        return fines[min(current_warnings, len(fines) - 1)]

    return data["fine"]


class Warnings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id != config.WARNING_CHANNEL:
            return

        if len(message.mentions) == 0:
            return

        member = message.mentions[0]
        warning_type = get_warning_type(message.content)

        if warning_type is None:
            return

        fine = calculate_fine(member.id, warning_type)

        database.add_warning(
            member.id,
            message.author.id,
            warning_type,
            fine
        )

        database.add_balance(member.id, -fine)

        total_warnings = database.get_warning_count(member.id)

        await message.add_reaction("✅")

        await message.reply(
            f"⚠️ **Warning procesado correctamente**\n\n"
            f"Usuario: {member.mention}\n"
            f"Tipo: **{warning_type}**\n"
            f"Warning nº: **{total_warnings}**\n"
            f"Multa aplicada: **{fine:,}**\n"
            f"Balance añadido: **-{fine:,}**"
        )

        await send_log(
            self.bot,
            "⚠️ Warning procesado",
            f"Usuario: {member.mention}\n"
            f"Moderador: {message.author.mention}\n"
            f"Tipo: {warning_type}\n"
            f"Warning nº: {total_warnings}\n"
            f"Multa: {fine:,}",
            discord.Color.orange()
        )

    @commands.command(name="warnings")
    async def warnings(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        warnings = database.get_warnings(member.id)

        if not warnings:
            await ctx.send(f"✅ {member.mention} no tiene warnings.")
            return

        total_fines = sum(row[2] for row in warnings)

        lines = [
            f"⚠️ **Warnings de {member.display_name}**",
            f"Total warnings: **{len(warnings)}**",
            f"Total multas: **{total_fines:,}**",
            ""
        ]

        for warning_id, reason, fine, created_at in warnings[:10]:
            lines.append(
                f"#{warning_id} | **{fine:,}** | {reason} | {created_at}"
            )

        await ctx.send("\n".join(lines))

    @commands.command(name="removewarning")
    @commands.has_permissions(administrator=True)
    async def removewarning(self, ctx, member: discord.Member):
        fine = database.remove_last_warning(member.id)

        if fine is None:
            await ctx.send(f"❌ {member.mention} no tiene warnings.")
            return

        database.add_balance(member.id, fine)

        await ctx.send(
            f"✅ Último warning eliminado de {member.mention}\n"
            f"Se le han devuelto **{fine:,}** al balance."
        )

        await send_log(
            self.bot,
            "✅ Warning eliminado",
            f"Usuario: {member.mention}\n"
            f"Eliminado por: {ctx.author.mention}\n"
            f"Balance devuelto: {fine:,}",
            discord.Color.green()
        )


async def setup(bot):
    await bot.add_cog(Warnings(bot))