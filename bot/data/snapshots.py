# Other imports
import os
import json


def get_player_snapshots() -> list:

    snapshots: list = []

    files: list = os.listdir("playerSnapshots")
    
    for file in files:
        with open(f"playerSnapshots/{file}", "r") as f:
            snapshots.append(json.load(f))

    return snapshots