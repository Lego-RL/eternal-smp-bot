# Project imports
import util.nbt as nbt
import util.player as player

# Other imports
import os
from sys import platform

# FILE_DATA = "the_vault_PlayerProficiency.dat"
if platform != "win32":
    FILE_DATA = os.path.join("world", "data", "the_vault_PlayerProficiency.dat")

else:
    FILE_DATA = os.path.join("local", "dats", "the_vault_PlayerProficiency.dat")


def get_player_proficiency_data(username: str):
    """
    Returns a dictionary of a single player's proficiency values.
    """

    nbt_data = nbt.read_nbt(FILE_DATA)

    # Retrieve player UUID
    playerUUID = player.get_uuid_from_username(username)

    # Guard clause
    if not playerUUID:
        return None
    
    prof_data: dict = {}
    
    for prof in nbt_data["data"][playerUUID]:
        prof_name = prof.title()

        prof_value: int = nbt_data['data'][playerUUID][prof].value
        prof_value_str: str = f"{prof_value / 100}%"

        prof_data[prof_name] = prof_value_str
    
    return prof_data