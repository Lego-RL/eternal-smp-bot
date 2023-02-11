# Project Imports
from image import EmbedWithImage, get_player_head_file_ign

# Other imports
import discord
from typing import Union

def get_bounty_embed(title: str, player_bounty_data: list, ign: str) -> EmbedWithImage:
    """
    Return an embed with given title and data on
    bounties in given bounty list.
    """

    embed: discord.Embed = discord.Embed(title=title)
    embed.color = 0x7c1bd1

    head_render: Union[discord.File, None] = get_player_head_file_ign(ign)
    if head_render:
        embed.set_thumbnail(url="attachment://image.png")

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

            # add newlines + invisible character after every bounty
            # then delete final newlines/invis character afterward
            field_str += "\n‎\n"

        if field_str:
            field_str = field_str[:-3]
        embed.add_field(name=f"{availability}".title(), value=field_str, inline=False)

    embed_obj: EmbedWithImage = EmbedWithImage(embed, head_render)
    return embed_obj