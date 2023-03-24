# Project imports
import util.player as player

# Other Imports
import discord
import os
import requests
import shutil
from sys import platform
from typing import Union

if platform != "win32":
    file_path: str = os.path.join("eternal-smp-bot", "images", "heads")

else:
    file_path: str = os.path.join("images", "heads")


class EmbedWithImage():
    """
    This image stores a created embed, as well as an
    optional discord.File field, so that functions in
    embeds.py can return an embed alongside a file
    for command functions to use. 

    This removes the necessity to pass the
    discord.ApplicationContext to each function
    in embeds.py, and to send the command
    response there.
    """

    def __init__(self, embed: discord.Embed, image_file: Union[discord.File, None]=None):
        self.embed: discord.Embed = embed
        self.image_file: Union[discord.File, None] = image_file



def download_player_head(uuid: str) -> bool:
    """
    Downloads an image of the given player's
    rendered minecraft head.

    Returns whether file was successfully
    downloaded or not.
    """

    # update to use standardized utils file later

    
    img_file_path = os.path.join(file_path, uuid)
    img_file_path += ".png"
    

    URL: str = f"https://crafatar.com/renders/head/{uuid}?overlay"

    response = requests.get(URL, stream=True)

    if response.status_code == 200:
        with open(img_file_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)

        return True
    
    else:
        return False


def is_player_head_saved(uuid: str) -> bool:
    """
    Return whether or not a player's head render
    is saved or not.
    """

    return f"{uuid}.png" in os.listdir(file_path)


def get_player_head_file(uuid: str) -> Union[discord.File, None]:
    """
    Returns discord.File object representing an image
    of the requested player's head rendering.
    """

    result: bool = True
    
    if not is_player_head_saved(uuid):
        result = download_player_head(uuid)

    if not result:
        return None
    
    img_file_path = os.path.join(file_path, uuid)
    img_file_path += ".png"
    
    with open(img_file_path, 'rb') as f:
        head_render: discord.File = discord.File(f, filename="image.png")
        return head_render
    

def get_player_head_file_ign(username: str) -> Union[discord.File, None]:
    """
    Helper function to bypass the need to convert all igns to UUIDs
    wherever player head file is needed.
    """

    player_uuid: Union[str, None] = player.get_uuid_from_username(username)

    if player_uuid:
        return get_player_head_file(player_uuid)


if __name__ == "__main__":
    download_player_head("3ac8e54e261a4ce9aa97cc7866f4242b")