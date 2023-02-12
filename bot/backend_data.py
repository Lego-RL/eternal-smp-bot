import json
import os
from sys import platform

import python_nbt.nbt as nbt

import util.uuid as uuid
from main import TESTING

if platform != "win32":
    if TESTING == False:
        VAULT_LANG_PATH: str = os.path.join("eternal-smp-bot", "lang", "the_vault.json")
        OTHER_PATH: str = os.path.join("eternal-smp-bot", "lang", "other.json")
    else:
        VAULT_LANG_PATH: str = os.path.join("test-eternal-smp-bot", "lang", "the_vault.json")
        OTHER_PATH: str = os.path.join("test-eternal-smp-bot", "lang", "other.json")

else:
    VAULT_LANG_PATH: str = os.path.join("lang", "the_vault.json")
    OTHER_PATH: str = os.path.join("lang", "other.json")


def get_bm_nbt_file():
    """
    Return NBT file for black market info.
    """

    if platform != "win32":
        path: str = os.path.join("world", "data", "the_vault_PlayerBlackMarket.dat")

    else:
        path: str = os.path.join("local", "dats", "the_vault_PlayerBlackMarket.dat")

    return nbt.read_from_nbt_file(path)


def format_bm_item_id(item_id: str):
    """
    Given a minecraft item id, return its
    user-facing display name.
    """

    if item_id == "minecraft:elytra":
        return "Elytra"
    
    # modify item_id to normalize with all id names
    normalized_item_id: str = "item." + (item_id).replace(":", ".")
    
    with open(VAULT_LANG_PATH, "r") as f:

        the_vault_data: dict = json.load(f)

        if normalized_item_id in the_vault_data.keys():
            item_display_name = the_vault_data.get(normalized_item_id) #type: ignore
            return item_display_name
    
    # fall back incase item not found in lang file
    return item_id


def get_bm_player_order() -> list:
    """
    Return a list of player names, in order, to
    match with proper black market data.
    """

    file = get_bm_nbt_file()

    uuid_dict: dict = uuid.get_uuid_username_dict()
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

            item: str = format_bm_item_id(trade["trade"]["stack"]["id"].value) #type: ignore
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

