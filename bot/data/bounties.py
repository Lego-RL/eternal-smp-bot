# Project imports
import util.uuid as uuid
import util.format as format

# Other imports
import os
from sys import platform
import python_nbt.nbt as nbt
import json



# Initiate files relating to bounties
files = {
    "data": "",
    "lang": ""
}

if platform != "win32":
    files["data"] = os.path.join("world", "data", "the_vault_Bounties.dat")
    files["lang"] = os.path.join("eternal-smp-bot", "lang", "bounties.json")
else:
    files["data"] = os.path.join("local", "dats", "the_vault_Bounties.dat")
    files["lang"] = os.path.join("lang", "bounties.json")



def get_file(requested_file: str = None) -> str:
    """
    Return the path of a requested file
    """
    return files[requested_file]


def get_bounty_player_order() -> list:
    """
    Return a list of player names, in order, to
    match with proper bounty data
    """

    file = nbt.read_from_nbt_file(get_file("data"))

    uuid_dict: dict = uuid.get_uuid_username_dict()
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


def get_player_bounty_data(ign: str):
    """
    Return the bounty data for an individual player
    """

    # Retrieve bounty file
    bounties_file = nbt.read_from_nbt_file(get_file("data"))

    # Retrieve player UUID
    playerUUID = uuid.get_uuid_from_ign(ign)

    # Guard clause
    if not playerUUID:
        return None

    # Initiate bounty list
    bounty_list: list = []

    # Loop through bounty availabilities
    for bounty_availability in ["active", "available", "complete"]:

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

            with open(get_file("lang"), "r") as f:
                
                # Retrieve bounties.json data
                bounties_lang: dict = json.load(f)

                # Retrieve bounty variable
                bounty_task_id = bounty_task_details[bounties_lang["tasks"][bounty_task_type]["taskId"]].value #type: ignore
            
            # Pre-format ids
            bounty_task_id_prefix = "item."
            if bounty_task_id in ["the_vault:vault_bronze", "the_vault:vault_silver", "the_vault:vault_gold"]:
                bounty_task_id_prefix = "block."
            bounty_task_id = bounty_task_id_prefix + bounty_task_id.replace(":", ".") #type: ignore

            # Format ids
            bounty_task_id = format.format_id(
                bounty_task_id,
                [
                    {
                        "file_path": get_file("lang"),
                        "id_path": f"tasks.{bounty_task_type}.ids"
                    }
                ]
            )
            bounty_task_type = format.format_id(
                bounty_task_type,
                [
                    {
                        "file_path": get_file("lang"),
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
            
                # Pre-format ids
                bounty_reward_id_prefix = "item."
                if bounty_reward_id in ["the_vault:vault_bronze", "the_vault:vault_silver", "the_vault:vault_gold"]:
                    bounty_reward_id_prefix = "block."
                bounty_reward_id = bounty_reward_id_prefix + bounty_reward_id.replace(":", ".") #type: ignore
                
                # Format id
                bounty_reward['id'] = format.format_id(bounty_reward_id)

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