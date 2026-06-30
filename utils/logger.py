import discord
import config


async def send_log(bot, title, description, color=discord.Color.blue()):
    channel = bot.get_channel(config.LOG_CHANNEL)

    if channel is None:
        return

    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )

    await channel.send(embed=embed)