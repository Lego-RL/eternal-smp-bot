import json
import os
from sys import platform

import python_nbt.nbt as nbt

if platform != "win32":
    BOUNTIES_LANG_PATH: str = os.path.join("eternal-smp-bot", "lang", "bounties.json")
    VAULT_LANG_PATH: str = os.path.join("eternal-smp-bot", "lang", "the_vault.json")

else:
    BOUNTIES_LANG_PATH: str = os.path.join("lang", "bounties.json")
    VAULT_LANG_PATH: str = os.path.join("lang", "the_vault.json")





def get_player_snapshots() -> list:

    snapshots: list = []

    files: list = os.listdir("playerSnapshots")
    
    for file in files:
        with open(f"playerSnapshots/{file}", "r") as f:
            snapshots.append(json.load(f))

    return snapshots


def get_uuid_from_ign(ign: str):
    """
    Return user's UUID given their ign
    """

    player_uuid_dict: dict = get_player_uuid_dict()

    for key, value in player_uuid_dict.items():
        if value == ign:
            return key


def get_player_uuid_dict() -> dict:
    """
    Return a dictionary of all players and their associated UUIDs.
    """

    snapshots: list = get_player_snapshots()
    player_uuids: dict = {}

    for snapshot in snapshots:
        player_uuids[snapshot["playerUUID"]] = snapshot["playerNickname"]

    return player_uuids


def get_bm_nbt_file():
    """
    Return NBT file for black market info.
    """

    if platform != "win32":
        path: str = os.path.join("world", "data", "the_vault_PlayerBlackMarket.dat")

    else:
        path: str = os.path.join("local", "dats", "the_vault_PlayerBlackMarket.dat")

    return nbt.read_from_nbt_file(path)

def get_bm_player_order() -> list:
    """
    Return a list of player names, in order, to
    match with proper black market data.
    """

    file = get_bm_nbt_file()

    uuid_dict: dict = get_player_uuid_dict()
    player_order: list = []

    for uuid in file["data"]["playerList"].value:
        player_order.append(uuid_dict[uuid.value])

    return player_order

def get_all_bm_data() -> dict:
    """
    Return data on everyone's current black market selection
    """

    file = get_bm_nbt_file()
    player_order: list = get_bm_player_order()

    bm_data: dict = {}

    for bm_entry, player in zip(file["data"]["blackMarketList"].value, player_order):

        if player not in bm_data:
            bm_data[player] = {
                "trades": [],
                "reset": None
            }

        bm_data[player]["reset"] = bm_entry["nextReset"].value

        for trade in bm_entry["trades"]:

            item: str = trade["trade"]["stack"]["id"].value
            amount: int = trade["trade"]["stack"]["Count"].value
            cost: int = trade["trade"]["cost"].value

            trade: dict = {
                item: {
                "amount": amount, 
                "cost": cost
                }
            }


            bm_data[player]["trades"].append(trade)

    return bm_data


def get_player_bm_data(ign: str) -> dict:
    """
    Return BM data on individual player.
    """

    bm_data: dict = get_all_bm_data()

    return bm_data[ign]


########### BOUNTY FUNCTIONS ###########

def format_bounty_task_id(bounty_id: str, bounty_type: str):

    # Check 'bounties.json' for name formatting
    with open(BOUNTIES_LANG_PATH, "r") as f:

        bounties_data: dict = json.load(f)
        
        if bounty_type in bounties_data.get("tasks").keys(): #type: ignore
            bounty_id = (bounties_data.get("tasks").get(bounty_type).get("idPrefix") + bounty_id).replace(":", ".") #type: ignore
            if bounty_id in bounties_data.get("tasks").get(bounty_type).get("ids"): #type: ignore
                bounty_id = bounties_data.get("tasks").get(bounty_type).get("ids").get(bounty_id) #type: ignore
                return bounty_id


    # Check 'the_vault.json' for name formatting
    with open(VAULT_LANG_PATH, "r") as f:

        the_vault_data: dict = json.load(f)

        if bounty_id in the_vault_data.keys():
            bounty_id = the_vault_data.get(bounty_id) #type: ignore

    return bounty_id


# Format Bounty's task "type"
def format_bounty_task_type(bounty_type: str):

    with open(BOUNTIES_LANG_PATH, "r") as f:

        bounties_data: dict = json.load(f)

        if bounty_type in bounties_data.get("tasks").keys(): #type: ignore
            bounty_type = bounties_data.get("tasks").get(bounty_type).get("name") #type: ignore

    return bounty_type


# Format Bounty's reward "id"
def format_bounty_reward_id(bounty_id: str):

    # Format properly
    bounty_prefix = "item."
    if bounty_id in ["the_vault:vault_bronze", "the_vault:vault_silver", "the_vault:vault_gold"]:
        bounty_prefix = "block."
    bounty_id = bounty_prefix + bounty_id.replace(":", ".") #type: ignore

    # Check 'bounties.json' for name formatting
    with open(BOUNTIES_LANG_PATH, "r") as f:

        bounties_data: dict = json.load(f)
        
        if bounty_id in bounties_data.get("rewards").keys(): #type: ignore
            bounty_id = bounties_data.get("rewards").get(bounty_id) #type: ignore
            return bounty_id


    # Check 'the_vault.json' for name formatting
    with open(VAULT_LANG_PATH, "r") as f:

        the_vault_data: dict = json.load(f)

        if bounty_id in the_vault_data.keys():
            bounty_id = the_vault_data.get(bounty_id) #type: ignore

    return bounty_id


def get_bounty_nbt_file():
    """
    Return NBT file for bounty info.
    """

    if platform != "win32":
        path: str = os.path.join("world", "data", "the_vault_Bounties.dat")

    else:
        path: str = os.path.join("local", "dats", "the_vault_Bounties.dat")

    return nbt.read_from_nbt_file(path)


def get_bounty_player_order() -> list:
    """
    Return a list of player names, in order, to
    match with proper bounty data.
    """

    file = get_bounty_nbt_file()

    uuid_dict: dict = get_player_uuid_dict()
    player_order: list = []

    for uuid in file["data"]["active"].value:
        player_order.append(uuid_dict[uuid])

    return player_order


def get_all_bounty_data() -> dict:
    """
    Return data on everyone's current bounty selection
    """

    bounty_player_order: list = get_bounty_player_order()

    bounty_data: dict = {}

    for player in bounty_player_order:
        bounty_data[player] = get_player_bounty_data(player)

    return bounty_data


def get_player_bounty_data(ign: str):
    """
    Return the bounty data for an individual player.
    """
    # Read files
    # bountiesFile = nbt.read_from_nbt_file("./files/the_vault_Bounties.dat")
    bountiesFile = get_bounty_nbt_file()


    # Retrieve variables
    playerUUID = get_uuid_from_ign(ign)

    if not playerUUID:
        return None

    bounties: list = []

    # Loop through active bounties
    for bounty_availability in ["active", "available", "complete"]:
        for bounty in bountiesFile['data'][bounty_availability][playerUUID].value: #type: ignore

            # Get Bounty
            bounty_details = bounty['task']

            if bounty_availability == "active":
                bounty_progress: int = bounty_details["amountObtained"].value

            ## Bounty Task
            bounty_task: str = bounty_details['properties']

            bounty_task_type: str = bounty_task['taskType'].value #type: ignore
            bounty_task_amount: int = round(bounty_task['amount'].value) #type: ignore
            bounty_task_id: str

            with open(BOUNTIES_LANG_PATH, "r") as f:

                bounties_data: dict = json.load(f)
                bounty_task_id = bounty_task[bounties_data.get("tasks").get(bounty_task_type).get("taskId")].value #type: ignore
            

            ### Format Names
            bounty_task_id = format_bounty_task_id(bounty_task_id, bounty_task_type)
            bounty_task_type = format_bounty_task_type(bounty_task_type)


            ## Bounty Rewards
            bounty_reward: str = bounty_details['reward']

            bounty_rewards: list = []

            for item in bounty_reward['items'].value: #type: ignore

                # exists will be True if bounty reward already exists in bounty_rewards list,
                # so as to not duplicate the entry
                exists: bool = False

                #check if reward is duplicated, and add to original entry count if so
                item_id: str = format_bounty_reward_id(item['id'].value)
                for index in range(len(bounty_rewards)):
                    if bounty_rewards[index]["id"] == item_id:
                        exists = True
                        bounty_rewards[index]["count"] += item['Count'].value

                # skip entries that already exist in bounty_rewards list
                if not exists:
                    bounty_rewards.append({
                        "id": format_bounty_reward_id(item['id'].value),
                        "count": item['Count'].value
                    })

            bounty_reward_experience = bounty_reward['vaultExp'].value #type: ignore
            
            bounty_dict: dict = {
                    "availability": bounty_availability,
                    "task": {
                        "type": bounty_task_type,
                        "amount": bounty_task_amount,
                        "id": bounty_task_id
                    },
                    "reward": {
                        "vaultExperience": bounty_reward_experience,
                        "items": bounty_rewards
                    }
                }
            
            if bounty_availability == "active":
                bounty_dict["task"]["progress"] = bounty_progress #type: ignore

            if bounty_availability == "complete":
                bounty_dict["expiration"] = bounty["expiration"].value

            bounties.append(bounty_dict)
            
    return bounties



if __name__ == "__main__":
    player_bounty_data = get_player_bounty_data("ubow")
    print(player_bounty_data)