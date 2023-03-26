# Project imports
import data.bounties as bounties
import data.crafted_modifiers as crafted_modifiers
from data.snapshots import get_player_snapshots
from data.black_market import get_player_black_market_data
from data.bounties import get_player_bounty_data
from embeds import get_bounty_embed
from image import EmbedWithImage

# Other imports
import discord
from discord import ApplicationContext

from discord.commands import slash_command, Option
from discord.ext import commands, tasks
from discord.interactions import Interaction

import json
import os
from sys import platform

TESTING = os.getenv("TESTING")

def has_alias_set():
    """
    Command decorator to check whether user has set their MC username alias.
    """
    def predicate(ctx):
        return str(ctx.user.id) in get_config_dict()

    return commands.check(predicate)


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

def get_config_dict() -> dict:
    """
    Retrieve config dict, containing info like discord -> mc username aliases,
    preferences on being alerted for new bounties, etc.
    """

    if platform != "win32":
        if TESTING == False:
            path: str = os.path.join("eternal-smp-bot", "bot", "config.json")
        else:
            path: str = os.path.join("test-eternal-smp-bot", "bot", "config.json")

    else:
        path: str = os.path.join("bot", "config.json")

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


def write_to_config_file(data: dict) -> None:
    """
    Standardized method to write a dict to
    the config file.
    """

    if platform != "win32":
        if TESTING == False:
            path: str = os.path.join("eternal-smp-bot", "bot", "config.json")
        else:
            path: str = os.path.join("test-eternal-smp-bot", "bot", "config.json")

    else:
        path: str = os.path.join("bot", "config.json")

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
    
    config: dict = get_config_dict()

    #filter out other config info
    aliases = {key: value["alias"] for key, value in config.items()}

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
        self.player_bounties: dict = {}

        self.bounty_alert_guild: discord.Guild = None #type: ignore
        self.bounty_alert_channel: discord.TextChannel = None #type: ignore



    @commands.Cog.listener()
    async def on_ready(self):
        """
        Begin bounty reminder task loop 
        """

        # Eternal SMP guild ID
        self.bounty_alert_guild = self.bot.get_guild(1064745467663102043) #type: ignore
        self.bounty_alert_channel = self.bounty_alert_guild.get_channel(1070115776637444197) #type: ignore

        self.bounty_alerts_task.start()

    def cog_unload(self):
        self.bounty_alerts_task.cancel()

    
    @tasks.loop(seconds=20)
    async def bounty_alerts_task(self):
        """
        Check if any players have received new bounties, 
        """

        config: dict = get_config_dict()

        # first run of task loop, initialize player bounties & wait for next loop
        if not self.player_bounties:
            for player_discord_id in config:
                mc_user: str = config[player_discord_id]["alias"]
                self.player_bounties[player_discord_id] = bounties.get_player_bounty_data(mc_user)

            # print(f"now {self.player_bounties=}")
            return

        for player_discord_id in config:
            mc_user: str = config[player_discord_id]["alias"]

            # if user bounties not initialized, as they just opted in to alerts, initialize & move on to next user
            if player_discord_id not in self.player_bounties:
                self.player_bounties[player_discord_id] = bounties.get_player_bounty_data(mc_user)
                continue

            # if user has alerts on
            if config[player_discord_id]["bounty_alerts"]:
                current_bounty_data: list = bounties.get_player_bounty_data(mc_user) #type: ignore
                # if no bounty data on player, skip them
                if not current_bounty_data:
                    break

                #if anything in their bounty list has changed since last snapshot
                if (stored_bounty_data := self.player_bounties[player_discord_id]) != current_bounty_data:

                    stored_bounty_rewards_lists: list = [bounty["reward"]["items"] for bounty in stored_bounty_data]
                    current_bounty_rewards_lists: list = [bounty["reward"]["items"] for bounty in current_bounty_data]
                    
                    # find what bounties are new
                    new_bounties = []
                    for i, bounty in enumerate(current_bounty_rewards_lists):
                        # if bounty, matched on rewards list, is one of the bounties previously stored
                        if any(bounty == stored_bounty for stored_bounty in stored_bounty_rewards_lists):
                            continue

                        # if user has already accepted or completed bounty, no need to alert them for it
                        elif current_bounty_data[i]["availability"] != "available":
                            continue
                        
                        # bounty doesn't match previously stored ones so it's new
                        else:
                            new_bounties.append(current_bounty_data[i])

                    # update player bounty data so new bounty is no longer seen as new
                    self.player_bounties[player_discord_id] = get_player_bounty_data(mc_user)

                    # if some bounty was different but none had different rewards, aka there
                    # are no bounties in the new_bounties list, then no need to alert
                    if not new_bounties:
                        return

                    # inform user of their new bounty/bounties
                    title: str = f"{mc_user}'s New Bounty" if len(new_bounties) == 1 else f"{mc_user}'s New Bounties"
                    embed_obj: EmbedWithImage = get_bounty_embed(title, new_bounties, mc_user) #problematic

                    if config[player_discord_id]["bounty_alert_pings"]:
                        player_discord: discord.User = await self.bot.fetch_user(int(player_discord_id)) #type: ignore
                        if embed_obj.image_file:
                            await self.bounty_alert_channel.send(player_discord.mention, file=embed_obj.image_file, embed=embed_obj.embed)
                        else:
                            await self.bounty_alert_channel.send(player_discord.mention, embed=embed_obj.embed)
                    else:
                        if embed_obj.image_file:
                            await self.bounty_alert_channel.send(file=embed_obj.image_file, embed=embed_obj.embed)
                        else:
                            await self.bounty_alert_channel.send(embed=embed_obj.embed)



    @has_alias_set()
    @slash_command(name="bounty-alerts")
    async def bounty_alerts(self, ctx: ApplicationContext, enabled: bool, 
                            ping: Option(bool, "Receieve pings when you have new bounties", required=False)): #type: ignore
        """
        Opt in to receive alerts when you have new bounties.
        """

        config: dict = get_config_dict()

        config[str(ctx.user.id)]["bounty_alerts"] = enabled
        config[str(ctx.user.id)]["bounty_alert_pings"] = ping

        write_to_config_file(config)

        await ctx.respond(f"Successfully opted {'in to' if enabled else 'out of'} bounty alerts.")



    # PLAYER SPECIFIC SLASH COMMANDS

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

        player_bm_data: dict = get_player_black_market_data(ign)

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

        player_bounty_data: list = bounties.get_player_bounty_data(ign) #type: ignore

        embed_obj: EmbedWithImage = get_bounty_embed(f"{ign}'s Bounties", player_bounty_data, ign)

        if embed_obj.image_file:
            await ctx.respond(file=embed_obj.image_file, embed=embed_obj.embed)

        else:
            await ctx.respond(embed=embed_obj.embed)


    @slash_command(name="crafted-modifiers")
    async def crafted_modifiers(self,
                       ctx: ApplicationContext,
                       user: Option(discord.User, "Choose a user to retrieve crafted modifier stats for", required=False), #type: ignore
                       mc_username: Option(str, "Choose a Minecraft username to retrieve crafted modifier stats for", required=False)): #type: ignore

        """
        Display the discovered crafted modifiers for a user / Minecraft username.
        """

        result_bool, result_str = choose_correct_ign(ctx, user, mc_username)

        # if couldn't find ign
        if not result_bool:
            await ctx.respond(result_str)
            return

        ign: str = result_str

        player_crafted_modifiers: list = crafted_modifiers.get_crafted_modifiers(ign) #type: ignore

        embed: discord.Embed = discord.Embed(title=f'{ign}\'s Crafted Modifiers')
        embed.color = 0x7c1bd1

        # Loop through vault gear pieces
        for vault_gear in player_crafted_modifiers:

            # Initiate field string
            field_string = ''
            
            # Loop through vault gear crafted modifiers
            for crafted_modifier in player_crafted_modifiers[vault_gear]:

                # Add modifier to field string (Soulbound)
                if 'Soulbound' in crafted_modifier['id']:
                    field_string += f'{crafted_modifier["id"]}'

                # Add modifier to field string (Single value)
                elif crafted_modifier["values"][0] == crafted_modifier["values"][1]:
                    field_string += f'{crafted_modifier["id"]}: {crafted_modifier["values"][0]}'
                
                # Add modifier to field string (other)
                else:
                    field_string += f'{crafted_modifier["id"]}: {crafted_modifier["values"][0]} - {crafted_modifier["values"][1]}'

                # Add empty line after every modifier
                field_string += f'\n'
            
            # Add field
            embed.add_field(name=f'{vault_gear}', value=f'{field_string}', inline=False)

        await ctx.respond(embed=embed)


def setup(bot: discord.Bot) -> None:
    bot.add_cog(Armory(bot))