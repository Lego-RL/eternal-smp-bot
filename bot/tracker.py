from armory import get_config_dict, write_to_config_file, has_alias_set

import discord
from discord import ApplicationContext

from discord.commands import slash_command, Option
from discord.ext import commands, tasks

import json
import os
from sys import platform

TESTING = os.getenv("TESTING")


def get_all_player_stats():
    """
    Return dictionary containing all playerSnapshots directory
    json data.
    """

    directory: str = "playerSnapshots"
    files: list = os.listdir(directory)

    data: dict = dict()

    for file in files:
        with open(os.path.join(directory, file)) as f:

            player_data: dict = json.load(f)
            player_name: str = player_data["playerNickname"]

            data[player_name] = player_data

    return data
    

class Tracker(commands.Cog):

    def __init__(self, bot: discord.Bot) -> None:
        self.bot: discord.Bot = bot
        self.eternal_guild_id: int = 1064745467663102043
        self.eternal_guild = None


    @commands.Cog.listener()
    async def on_ready(self):
        """
        Begin level updating task loop 
        """

        self.eternal_guild = self.bot.get_guild(self.eternal_guild_id)

        self.update_player_level_task.start()

    def cog_unload(self):
        self.update_player_level_task.cancel()


    @tasks.loop(seconds=60)
    async def update_player_level_task(self):
        """
        Keep discord usernames up to date with current level
        of players who opt in.
        """

        if not self.eternal_guild:
            return

        config_data: dict = get_config_dict()
        all_player_stats: dict = get_all_player_stats()

        for discord_id, config in config_data.items():
            
            if config.get("track_level_nick"):
                discord_user = await self.eternal_guild.fetch_member(discord_id)
                mc_username: str = config.get("alias")
                
                # move on if failed to retrieve discord user obj
                if not isinstance(discord_user, discord.Member):
                    continue

                # move on if player not stored in all_player_stats
                if not (player_stats := all_player_stats.get(mc_username)):
                    continue

                # move on if failed to retrieve vault level
                if not isinstance((vault_level := player_stats.get("vaultLevel")), int):
                    continue

                vault_level = str(vault_level)
                user_nick: str = discord_user.display_name
                pipe_loc: int = user_nick.find(" |")

                # truncate level off nick if already exists
                if pipe_loc != -1:
                    user_nick = user_nick[:pipe_loc]

                updated_username: str = user_nick + f" | {vault_level}"
                total_user_len: int = len(updated_username)

                # make sure nick is within 32 chars to be valid discord nick
                if total_user_len > 32:
                    to_truncate: int = total_user_len - 32
                    updated_username = user_nick[:-to_truncate] + f" | {vault_level}"

                await discord_user.edit(nick=updated_username)


    @has_alias_set()
    @slash_command(name="enable-nick-level")
    async def enable_nick_level(self, ctx: ApplicationContext, enabled: bool):
        """
        Opt in to have nickname updated with vault level.
        """

        if ctx.guild.owner_id == ctx.user.id: #type: ignore
            await ctx.respond("Bots are unable to change owner's nickname!")
            return

        configs: dict = get_config_dict()

        try:
            configs[str(ctx.user.id)]["track_level_nick"] = enabled #type: ignore
            write_to_config_file(configs)

        except KeyError:
            await ctx.respond("Unable to store config!", ephemeral=True)
            return
        
        if enabled:
            choice_str: str = "Your nickname will now be kept up to date with your vault level."

        else:
            choice_str = "Your nickname will not be kept up to date with your vault level."
        
        await ctx.respond(f"Properly stored your setting! {choice_str}", ephemeral=True)


    @enable_nick_level.error
    async def on_enable_nick_error(self, ctx: ApplicationContext, error): #type: ignore
        if isinstance(error, discord.errors.CheckFailure):
            await ctx.respond("You must have your alias set with `/alias` use this command!", ephemeral=True)
        else:
            raise error
        

def setup(bot: discord.Bot) -> None:
    bot.add_cog(Tracker(bot))
