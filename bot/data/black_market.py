# Project imports
import util.format as format
import util.nbt as nbt
import util.uuid as uuid

# Other imports
from sys import platform
import os


uuid.get_uuid_username_dict

# Initiate files relating to bounties
FILE_DATA = ""

if platform != "win32":
    FILE_DATA = os.path.join("world", "data", "the_vault_PlayerBlackMarket.dat")

else:
    FILE_DATA = os.path.join("local", "dats", "the_vault_PlayerBlackMarket.dat")




def get_black_market_player_order() -> list:
    """
    Return a list of player names, in order, to match with proper black market data.
    """

    file = nbt.read_nbt(FILE_DATA)

    uuid_dict: dict = uuid.get_uuid_username_dict()
    player_order: list = []

    for player_uuid in file["data"]["playerList"].value:
        player_order.append(uuid_dict[player_uuid.value])

    return player_order


def get_all_black_market_data() -> dict:
    """
    Return Black Market data on every player
    """

    file = nbt.read_nbt(FILE_DATA)
    player_order: list = get_black_market_player_order()

    bm_data: dict = {}

    for bm_entry, player in zip(file["data"]["blackMarketList"].value, player_order):

        if player not in bm_data:
            bm_data[player] = {
                "trades": [],
                "reset": None
            }

        bm_data[player]["reset"] = bm_entry["nextReset"].value

        for trade in bm_entry["trades"]:

            item: str = format.format_id(format.preformat_id(trade["trade"]["stack"]["id"].value)) #type: ignore
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


def get_player_black_market_data(ign: str) -> dict:
    """
    Return Black Market data on individual player
    """

    bm_data: dict = get_all_black_market_data()

    return bm_data[ign]