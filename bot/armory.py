import discord
from discord import ApplicationContext

from discord.commands import slash_command, Option
from discord.ext import commands

import json
import os
from sys import platform

from backend_data import get_player_snapshots, get_player_bm_data, get_player_bounty_data


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

def get_alias_dict() -> dict:
    """
    Retrieve list of aliases, of mc username to discord user ids.
    """

    if platform != "win32":
        path: str = os.path.join("eternal-smp-bot", "bot", "alias.json")

    else:
        path: str = os.path.join("bot", "alias.json")

    if not os.path.isfile(path):
        # generate file if it doesn't already exist
        with open(path, "w") as f:
            pass

    with open(path, "a+") as f:
        f.seek(0)

        try:
            data: dict = json.load(f)

        except json.JSONDecodeError:
            return {}

    return data


def write_to_alias_file(data: dict) -> None:
    """
    Standardized method to write a dict to
    the alias file.
    """

    if platform != "win32":
        path: str = os.path.join("eternal-smp-bot", "bot", "alias.json")

    else:
        path: str = os.path.join("bot", "alias.json")

    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def choose_correct_ign(ctx: ApplicationContext, user=None, mc_username=None) -> tuple:
    """
    Return tuple of bool, str.

    Bool represents whether proper username was found or not, if
    found then str will represent players IGN.

    If not found, str will be proper error message to display to user.
    """

    if mc_username:
        return (True, mc_username)
    
    aliases: dict = get_alias_dict()

    if user:
        if str(user.id) in aliases:
            return (True, aliases[str(user.id)])

        else:
            return (False, "Could not find user's alias! Have they set their alias with `/alias`?")
        
    else:
        if str(ctx.user.id) in aliases:
            return (True, aliases[str(ctx.user.id)])

        else:
            return (False, "Could not find your alias! Have you set your alias with `/alias`?")


class Armory(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot: discord.Bot = bot

    # PLAYER SPECIFIC SLASH COMMNADS

    @slash_command(name="stats")
    async def stats(self, 
                    ctx: ApplicationContext, 
                    user: Option(discord.User, "Choose a user to look up stats for", required=False), #type: ignore
                    mc_username: Option(str, "Alternatively, supply a Minecraft username to get stats on", required=False)): #type: ignore
        """
        Respond with an embed of player stats on the requested player.
        """

        result_bool, result_str = choose_correct_ign(ctx, user, mc_username)

        # if couldn't find ign
        if not result_bool:
            await ctx.respond(result_str)
            return

        ign: str = result_str

        stats: dict = get_player_stats(ign)

        if not stats:
            await ctx.respond("Could not find a player with given Minecraft username!",)
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
        embed.color = 0x7c1bd1

        embed.add_field(name="Abilities", value=abilities_str, inline=True)
        embed.add_field(name='Talents', value=talents_str, inline=True)
        embed.add_field(name='Researches', value=researches_str, inline=False)

        await ctx.respond(embed=embed)
            

    @slash_command(name="bm")
    async def black_market(self, 
                           ctx: ApplicationContext, 
                           user: Option(discord.User, "Choose a user view active black market offerings for", required=False), #type: ignore
                           mc_username: Option(str, "Alternatively, supply a Minecraft username to get black market offerings", required=False)): #type: ignore
        """
        Display the available black market trades of given player.
        """

        result_bool, result_str = choose_correct_ign(ctx, user, mc_username)

        # if couldn't find ign
        if not result_bool:
            await ctx.respond(result_str)
            return

        ign: str = result_str

        player_bm_data: dict = get_player_bm_data(ign)

        embed: discord.Embed = discord.Embed(title=f"{ign}'s Black Market")
        embed.color = 0x7c1bd1

        sorted_trades = sorted(player_bm_data["trades"], key=lambda x:x[list(x.keys())[0]]["cost"], reverse=True)

        for trade in sorted_trades:
            item: str = list(trade.keys())[0]
            amount: int = trade[item]["amount"]
            cost: int = trade[item]["cost"]

            embed.add_field(name=f"x{amount} {item}", value=f"Costs {cost} soul shards", inline=False)

        await ctx.respond(embed=embed)


    @slash_command(name="bounty")
    async def bounties(self,
                       ctx: ApplicationContext,
                       user: Option(discord.User, "Choose a user to look up bounty stats for", required=False), #type: ignore
                       mc_username: Option(str, "Alternatively, supply a Minecraft username to get bounty stats on", required=False)): #type: ignore

        """
        Display available, active, and completed bounties of a given user.
        """

        result_bool, result_str = choose_correct_ign(ctx, user, mc_username)

        # if couldn't find ign
        if not result_bool:
            await ctx.respond(result_str)
            return

        ign: str = result_str

        player_bounty_data: list = get_player_bounty_data(ign) #type: ignore

        embed: discord.Embed = discord.Embed(title=f"{ign}'s Bounties")
        embed.color = 0x7c1bd1

        availability_set: set = set()

        for bounty in player_bounty_data:
            availability_set.add(bounty["availability"])

        # show categories in same order every time
        availability_order: list = ["active", "available", "complete"]
        availability_order = [x for x in availability_order if x in availability_set]

        index: int = 0
        for availability in availability_order:
            relevant_bounties: list = [bounty for bounty in player_bounty_data if bounty["availability"] == availability]

            field_str: str = ""

            for bounty in relevant_bounties:
                # task type
                field_str += f"**{bounty['task']['type']}**\n"

                # task id : amount
                bounty_progress: int = int(bounty["task"]["progress"]) if bounty["availability"] == "active" else 0
                field_str += f"{bounty['task']['id']}: {bounty_progress} / {bounty['task']['amount']}\n\n"
                
                # rewards
                rewards_str: str = ""
                for reward in bounty['reward']["items"]:
                    rewards_str += f"{reward['id']}: {reward['count']}, "

                rewards_str = rewards_str[:-2]

                rewards_str += f"\nExperience: {bounty['reward']['vaultExperience']}"

                field_str += f"Rewards: {rewards_str}"

                if bounty["availability"] == "complete":
                    # conversion to cut off last few numbers
                    expiry_timestamp: int = int(str(bounty["expiration"])[:10])

                    field_str += f"\n\nExpires at <t:{expiry_timestamp}:f>"

                if index < 2:
                    field_str += "\n‎\n"

                index += 1

            embed.add_field(name=f"{availability}".title(), value=field_str, inline=False)


        

        await ctx.respond(embed=embed)

    # PLAYER AGNOSTIC SLASH COMMANDS

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