import discord
from discord import ApplicationContext

from discord.commands import slash_command
from discord.ext import commands, tasks

import requests

def get_players_online() -> list:
    """
    Return a list of names of players currently
    online.
    """

    API_LINK: str = "https://api.mcsrvstat.us/2/150.136.42.152"

    response: dict = requests.get(API_LINK).json()

    players: list = response["players"]["list"]

    players = [player.strip("(vault)") for player in players]

    return players


class Info(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot: discord.Bot = bot

        self.eternal_guild_id: int = 1064745467663102043
        self.num_online_vc_id: int = 1070469112662335519

        self.eternal_guild = None
        self.num_online_vc = None
        


    @commands.Cog.listener()
    async def on_ready(self):
        """
        Fetch guild and voice channel objects when bot is ready.
        """

        self.eternal_guild = self.bot.get_guild(self.eternal_guild_id)
        if self.eternal_guild:
            self.num_online_vc = self.eternal_guild.get_channel(self.num_online_vc_id)

        self.update_num_online.start()

        
    @tasks.loop(seconds=30)
    async def update_num_online(self):
        """
        Automatically update a voice channel's name every
        30 seconds with how many players are currently online.
        """

        players: list = get_players_online()
        num_players: int = len(players)

        if self.num_online_vc:
            if num_players == 1:
                await self.num_online_vc.edit(name=f"{num_players} player online!")

            else:
                await self.num_online_vc.edit(name=f"{num_players} players online!")

    @slash_command(name="online")
    async def online(self, ctx: ApplicationContext):
        """
        Display what users are currently online.
        """

        players: list = get_players_online()

        if not players:
            await ctx.respond("There are currently no players online!")

        else:
            response_str: str = "**Players currently online**:" + "\n"
            await ctx.respond(response_str + "\n".join(players))


def setup(bot: discord.Bot) -> None:
    bot.add_cog(Info(bot))