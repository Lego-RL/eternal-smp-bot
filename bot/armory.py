import discord
from discord import ApplicationContext

from discord.commands import slash_command
from discord.ext import commands

import json
import os

def get_player_snapshots() -> list:

    snapshots: list = []

    files: list = os.listdir("playerSnapshots")
    
    for file in files:
        with open(f"playerSnapshots/{file}", "r") as f:
            snapshots.append(json.load(f))

    return snapshots

def get_player_stats(ign: str) -> dict:
    """
    Return dictionary of player stats, given a player name.
    """

    snapshots: list = get_player_snapshots()
    to_preserve: list = ["vaultLevel", "powerLevel", "abilities", "talents", "researches"]

    for snapshot in snapshots:
        if snapshot["playerNickname"] == ign:
            stats: dict = {key: snapshot[key] for key in snapshot if key in to_preserve}
            return stats

    return {}

    

class Armory(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot: discord.Bot = bot


    @slash_command(name="stats")
    async def stats(self, ctx: ApplicationContext, ign: str):
        """
        Respond with an embed of player stats on the requested player.
        """

        stats: dict = get_player_stats(ign)

        if not stats:
            await ctx.respond("Could not find a player with given username!",)
            return
        
        vaultLevel, powerLevel = stats["vaultLevel"], stats["powerLevel"]
        abilities_str: str = ""
        talents_str: str = ""
        researches_str: str = ""

        for ability, level in stats["abilities"].items():
            abilities_str += f"{ability}: {level}\n"

        for talent, level in stats["talents"].items():
            talents_str += f"{talent}: {level}\n"

        for research in stats["researches"]:
            researches_str += f"{research}\n"

        if not abilities_str:
            abilities_str = "This player has not taken any abilities!"

        if not talents_str:
            talents_str = "This player has not taken any talents!"

        if not researches_str:
            researches_str = "This player has researched no mods yet!"


        description: str = f"Vault level: **{vaultLevel}**\nPower level: **{powerLevel}**"
        embed: discord.Embed = discord.Embed(title=f"{ign}'s Stats", description=description)

        embed.add_field(name="Abilities", value=abilities_str, inline=True)
        embed.add_field(name='Talents', value=talents_str, inline=True)
        embed.add_field(name='Researches', value=researches_str, inline=False)

        await ctx.respond(embed=embed)
            



    @slash_command(name="in-vault")
    async def invault(self, ctx: ApplicationContext):
        """
        Respond with a list of players currently in a vault.
        """

        snapshots: list[dict] = get_player_snapshots()
        players_in_vault: list[str] = []

        for snapshot in snapshots:
            if snapshot["inVault"]:
                players_in_vault.append(snapshot["playerNickname"])

        if players_in_vault:
            await ctx.respond("Players currently in vault:\n" + "\n".join(players_in_vault))

        else:
            await ctx.respond("There are currently no players in a vault!")



if __name__ == "__main__":
    pass


def setup(bot: discord.Bot) -> None:
    bot.add_cog(Armory(bot))