import discord
from dotenv import load_dotenv

import os

load_dotenv()

TESTING = os.getenv("TESTING")

if TESTING == "TRUE" or TESTING == True:
    TOKEN = os.getenv("TEST_TOKEN")
else:
    TOKEN = os.getenv("BOT_TOKEN")



bot = discord.Bot()

@bot.event
async def on_ready():
    """
    Log the bot being properly online.
    """

    print(f"{bot.user} has connected to Discord!")


if __name__ == "__main__":

    extensions = ['admin', 'armory', 'info']

    for ext in extensions:
        bot.load_extension(ext)
    
    bot.run(TOKEN)
