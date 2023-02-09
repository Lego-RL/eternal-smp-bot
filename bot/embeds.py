import discord

def get_bounty_embed(title: str, player_bounty_data: list, ign: str) -> discord.Embed:
    """
    Return an embed with given title and data on
    bounties in given bounty list.
    """

    embed: discord.Embed = discord.Embed(title=title)
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

    return embed