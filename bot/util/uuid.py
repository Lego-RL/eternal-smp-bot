# Project imports
import data.snapshots as snapshots

def get_uuid_from_ign(ign: str):
    """
    Return user's UUID given their ign
    """

    player_uuid_dict: dict = get_uuid_username_dict()

    for key, value in player_uuid_dict.items():
        if value == ign:
            return key


def get_uuid_username_dict() -> dict:
    """
    Return a dictionary of all UUIDs and their associated players.
    """

    snapshots: list = snapshots.get_player_snapshots()
    player_uuids: dict = {}

    for snapshot in snapshots:
        player_uuids[snapshot["playerUUID"]] = snapshot["playerNickname"]

    return player_uuids