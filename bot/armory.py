import discord
from discord import ApplicationContext

from discord.commands import slash_command
from discord.ext import commands

class Armory(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot: discord.Bot = bot

    
    @slash_command(name="in-vault")
    async def invault(self, ctx: ApplicationContext):
        """
        Respond with a list of players currently in a vault.
        """

        



def setup(bot: discord.Bot) -> None:
    bot.add_cog(Armory(bot))