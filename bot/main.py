import discord
from dotenv import load_dotenv

import os

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")


bot = discord.Bot()


extensions = ['admin', 'armory', 'info']

for ext in extensions:
    bot.load_extension(ext)


@bot.event
async def on_ready():
    """
    Log the bot being properly online.
    """

    print(f"{bot.user} has connected to Discord!")


if __name__ == "__main__":
    bot.run(TOKEN)
