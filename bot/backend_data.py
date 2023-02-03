import json
import os
from sys import platform

import python_nbt.nbt as nbt

def get_player_snapshots() -> list:

    snapshots: list = []

    files: list = os.listdir("playerSnapshots")
    
    for file in files:
        with open(f"playerSnapshots/{file}", "r") as f:
            snapshots.append(json.load(f))

    return snapshots

def get_player_uuid_dict():
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

    bm_data: dict = {}

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

if __name__ == "__main__":
    bm_data = get_all_bm_data()
    for trade in bm_data["Drlegoman"]["trades"]:
        print(f"{trade}\n")

    print(f"Drlegoman's trades reset at {bm_data['Drlegoman']['reset']}")