# Project imports
import data.snapshots as snapshots

def get_uuid_from_username(username: str):
    """
    Return user's UUID given their username
    """

    player_uuid_dict: dict = get_uuid_username_dict()

    for key, value in player_uuid_dict.items():
        if value == username:
            return key


def get_uuid_username_dict() -> dict:
    """
    Return a dictionary of all UUIDs and their associated players.
    """

    snapshots_list: list = snapshots.get_player_snapshots()
    player_uuids: dict = {}

    for snapshot in snapshots_list:
        player_uuids[snapshot["playerUUID"]] = snapshot["playerNickname"]

    return player_uuids