# Project imports
import util.format as format
import util.nbt as nbt
import util.player as player
from main import TESTING

# Other imports
import os
from sys import platform
import json



# Initiate files relating to bounties
FILE_DATA = ""
FILE_LANG = ""

if platform != "win32":
    FILE_DATA = os.path.join("world", "data", "the_vault_Bounties.dat")
    if TESTING == False:
        FILE_LANG = os.path.join("eternal-smp-bot", "lang", "bounties.json")
    else:
        FILE_LANG = os.path.join("test-eternal-smp-bot", "lang", "bounties.json")

else:
    FILE_DATA = os.path.join("local", "dats", "the_vault_Bounties.dat")
    FILE_LANG = os.path.join("lang", "bounties.json")



def get_bounty_player_order() -> list:
    """
    Return a list of player names, in order, to
    match with proper bounty data
    """

    file = nbt.read_nbt(FILE_DATA)

    uuid_dict: dict = player.get_uuid_username_dict()
    player_order: list = []

    for player_uuid in file["data"]["active"].value:
        player_order.append(uuid_dict[player_uuid])

    return player_order


def get_all_bounty_data() -> dict:
    """
    Return the bounty data for all players
    """

    bounty_player_order: list = get_bounty_player_order()

    bounty_data: dict = {}

    for player in bounty_player_order:
        bounty_data[player] = get_player_bounty_data(player)

    return bounty_data


def get_player_bounty_data(username: str):
    """
    Return the bounty data for an individual player
    """

    # Retrieve bounty file
    bounties_file = nbt.read_nbt(FILE_DATA)

    # Retrieve player UUID
    playerUUID = player.get_uuid_from_username(username)

    # Guard clause
    if not playerUUID:
        return None

    # Initiate bounty list
    bounty_list: list = []

    # Loop through bounty availabilities
    for bounty_availability in ["legendary", "active", "available", "complete"]:

        # Check if bounty availability exists
        #if bounties_file['data'][bounty_availability] is None:
            #continue

        # Loop through bounties
        for bounty in bounties_file['data'][bounty_availability][playerUUID].value: #type: ignore

            # Get bounty details
            bounty_details = bounty['task']


            # Retrieve bounty task details
            bounty_task_details: str = bounty_details['properties']

            # Retrieve bounty task variables
            bounty_task_type: str = bounty_task_details['taskType'].value #type: ignore
            bounty_task_amount_obtained: int = bounty_details["amountObtained"].value
            bounty_task_amount: int = round(bounty_task_details['amount'].value) #type: ignore
            bounty_task_id: str

            with open(FILE_LANG, "r") as f:
                
                # Retrieve bounties.json data
                bounties_lang: dict = json.load(f)

                # Retrieve bounty variable
                bounty_task_id = bounty_task_details[bounties_lang["tasks"][bounty_task_type]["taskId"]].value #type: ignore
            
            # Pre-format ids
            bounty_task_id = format.preformat_id(bounty_task_id)

            # Format ids
            bounty_task_id = format.format_id(
                bounty_task_id,
                [
                    {
                        "file_path": FILE_LANG,
                        "id_path": f"tasks.{bounty_task_type}.ids"
                    }
                ]
            )
            bounty_task_type = format.format_id(
                bounty_task_type,
                [
                    {
                        "file_path": FILE_LANG,
                        "id_path": "tasks",
                        "name_path": f"tasks.{bounty_task_type}.name"
                    }
                ]
            )


            # Retrieve bounty reward details
            bounty_reward_details: str = bounty_details['reward']

            # Initiate bounty rewards
            bounty_rewards: list[dict] = []

            # Loop through reward items
            for bounty_reward in bounty_reward_details['items'].value: #type: ignore

                # Retrieve bounty reward variables
                bounty_reward_id: str = bounty_reward['id'].value
                bounty_reward_count: int = bounty_reward['Count'].value

                # Initiate reward boolean
                bounty_reward_exists: bool = False

                # Combine counts if reward is registered
                for index in range(len(bounty_rewards)):
                    if bounty_rewards[index]["id"] == bounty_reward_id:
                        bounty_reward_exists = True
                        bounty_rewards[index]["count"] += bounty_reward_count

                # Register reward
                if not bounty_reward_exists:
                    bounty_rewards.append({
                        "id": bounty_reward_id,
                        "count": bounty_reward_count
                    })

            # Format bounty rewards
            for bounty_reward in bounty_rewards:

                # Initiate variables
                bounty_reward_id = bounty_reward['id']
                
                # Format id
                bounty_reward['id'] = format.format_id(format.preformat_id(bounty_reward_id))

            # Sort bounty rewards by quantity
            bounty_rewards = sorted(bounty_rewards, key=lambda x: x["count"], reverse=True)

            # Retrieve bounty variables
            bounty_reward_experience = bounty_reward_details['vaultExp'].value #type: ignore
            
            # Bounty data
            bounty_dict: dict = {
                "availability": bounty_availability,
                "task": {
                    "type": bounty_task_type,
                    "amount_obtained": bounty_task_amount_obtained,
                    "amount": bounty_task_amount,
                    "id": bounty_task_id
                },
                "reward": {
                    "vault_experience": bounty_reward_experience,
                    "items": bounty_rewards
                }
            }

            # Retrieve bounty refresh time
            if bounty_availability == "complete":
                bounty_dict["refresh_time"] = bounty["expiration"].value

            # Add bounty to bounty list
            bounty_list.append(bounty_dict)
    
    
    # Return bounty list
    return bounty_list