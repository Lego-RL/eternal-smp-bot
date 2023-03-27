# Project Imports
from image import EmbedWithImage, get_player_head_file_ign

# Other imports
import discord
from enum import Enum
from typing import Union


class PlayerListOptions(Enum):
    ONLINE = 1
    IN_VAULT = 2

def get_starter_embed(title: str, ign: str) -> tuple:
    """
    Returns a basic embed with its thumbnail set to a given
    player's rendered head.
    """

    embed: discord.Embed = discord.Embed(title=title)
    embed.color = 0x7c1bd1

    head_render: Union[discord.File, None] = get_player_head_file_ign(ign)
    if head_render:
        embed.set_thumbnail(url="attachment://image.png")

    return (embed, head_render)


def get_bounty_embed(title: str, player_bounty_data: list, ign: str) -> EmbedWithImage:
    """
    Return an embed with given title and data on
    bounties in given bounty list.
    """

    embed, head_render = get_starter_embed(title, ign)

    availability_set: set = set()

    for bounty in player_bounty_data:
        if isinstance(bounty, list):
            availability_set.add(bounty[0]["availability"])

        else:
            availability_set.add(bounty["availability"])

    # show categories in same order every time
    availability_order: list = ["active", "available", "complete"]
    availability_order = [x for x in availability_order if x in availability_set]

    for availability in availability_order:
        relevant_bounties: list = [bounty for bounty in player_bounty_data if bounty["availability"] == availability]

        field_str: str = ""

        for bounty in relevant_bounties:
            # task type
            field_str += f"**{bounty['task']['type']}**\n"

            # task id : amount
            bounty_progress: int = int(bounty["task"]["amount_obtained"])
            field_str += f"{bounty['task']['id']}: {bounty_progress} / {bounty['task']['amount']}\n\n"
            
            # rewards
            rewards_str: str = ""
            for reward in bounty['reward']["items"]:
                rewards_str += f"{reward['id']}: {reward['count']}, "

            rewards_str = rewards_str[:-2]

            rewards_str += f"\nExperience: {bounty['reward']['vault_experience']}"

            field_str += f"Rewards: {rewards_str}"

            if bounty["availability"] == "complete":
                # conversion to cut off last few numbers
                expiry_timestamp: int = int(str(bounty["refresh_time"])[:10])

                field_str += f"\n\nRefreshes in <t:{expiry_timestamp}:f>"

            # add newlines + invisible character after every bounty
            # then delete final newlines/invis character afterward
            field_str += "\n‎\n"

        if field_str:
            field_str = field_str[:-3]
        embed.add_field(name=f"{availability}".title(), value=field_str, inline=False)

    embed_obj: EmbedWithImage = EmbedWithImage(embed, head_render)
    return embed_obj


def get_player_prof_embed(title: str, ign: str, prof_data) -> EmbedWithImage:
    """
    Return an embed with given title and data on
    a player's proficiency numbers.
    """

    embed, head_render = get_starter_embed(title, ign)

    desc_str: str = ""

    ORDER: tuple = ("Helmet", "Chestplate", "Leggings", "Boots", "Magnet", "Sword", "Axe", "Shield", "Idol")
    for prof_type in ORDER:

        prof_value = prof_data.get(prof_type)
        if prof_value:
            desc_str += f"__{prof_type}__ - {prof_value}\n"

    embed.description = desc_str

    embed_obj: EmbedWithImage = EmbedWithImage(embed, head_render)
    return embed_obj


def get_players_embed(list_option: PlayerListOptions, players: list) -> discord.Embed:
    """
    Returns an embed that lists all players
    currently representing given metric
    (i.e. online, in a vault).
    """

    if list_option == PlayerListOptions.ONLINE:
        title: str = "Players online"
        empty_description: str = "There are currently no players online!"

    elif list_option == PlayerListOptions.IN_VAULT:
        title: str = "Players in vault"
        empty_description: str = "There are currently no players in a vault!"

    embed: discord.Embed = discord.Embed(title=title)
    embed.color = 0x7c1bd1

    if not players:
        embed.description = empty_description
    else:
        embed.description = "\n".join(players)
    

    return embed

