import discord
from discord import ApplicationContext

from discord.commands import slash_command
from discord.ext import commands, tasks

import json
import requests

from armory import get_config_dict, write_to_config_file


def get_players_online() -> list:
    """
    Return a list of names of players currently
    online.
    """

    API_LINK: str = "https://api.mcsrvstat.us/2/150.136.42.152"
    players: list = []

    response: dict = requests.get(API_LINK).json()

    # sometimes player list is in "info", sometimes in "players"

    if resp_info := response.get("info"):
        if "clean" in resp_info.keys():
            players = response["info"]["clean"]

    elif resp_info := response.get("players"):
        if "list" in resp_info.keys():
            players = resp_info["list"]

    if not players:
        # no players online
        return []

    players = [player[:-7] if "(vault)" in player else player for player in players]

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

    def cog_unload(self):
        self.update_num_online.cancel()

    @tasks.loop(seconds=10)
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

    @slash_command(name="alias")
    async def set_alias(self, ctx: ApplicationContext, ign: str):
        """
        Allow a user to set their MC username.
        """
        data: dict = get_config_dict()

        if str(ctx.user.id) not in data:
            data[str(ctx.user.id)] = {
                "alias": ign,
                "bounty_alerts": False,
                "bounty_alert_pings": False
            }

        else:
            data[str(ctx.user.id)]["alias"] = ign

        write_to_config_file(data)

        await ctx.respond(
            f"Successfully tied your discord account to Minecraft user `{ign}`!"
        )


def setup(bot: discord.Bot) -> None:
    bot.add_cog(Info(bot))
