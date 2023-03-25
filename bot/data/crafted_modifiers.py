# Project imports
import util.config as config
import util.converter as converter
import util.format as format
import util.nbt as nbt
import util.player as player
from main import TESTING

# Other imports
import os
from sys import platform
import json



# Initiate files relating to crafted modifiers
FILE_DATA = ''
FILE_LANG = ''

if platform != "win32":
    FILE_DATA = os.path.join("world", "data", "the_vault_DiscoveredWorkbenchModifiers.dat")
    if TESTING == False:
        FILE_LANG = os.path.join("eternal-smp-bot", "lang", "crafted_modifiers.json")
    else:
        FILE_LANG = os.path.join("test-eternal-smp-bot", "lang", "crafted_modifiers.json")

else:
    FILE_DATA = os.path.join("local", "dats", "the_vault_DiscoveredWorkbenchModifiers.dat")
    FILE_LANG = os.path.join("lang", "crafted_modifiers.json")



def get_crafted_modifiers_data() -> dict:
    """
    Returns a dictionary of player names, with the corresponding discovered crafted modifiers 
    """

    # Retrieve nbt data
    nbt_data = nbt.read_nbt(FILE_DATA)

    # Initiate variables
    crafted_modifiers_data: dict = {}

    # Loop through entries
    for entry in nbt_data['data']['crafts'].value:

        # Initiate variables
        player_crafted_modifiers = entry['itemCrafts'].value
        player_uuid = entry['player'].value

        player_uuid_hex = ''

        for i in player_uuid:
           player_uuid_hex += f'{converter.tohex(i, 32).lstrip("0x")}'

        # Add data to dictionary
        crafted_modifiers_data[player_uuid_hex] = player_crafted_modifiers

    # Return data
    return crafted_modifiers_data


def get_crafted_modifiers(username: str):
    """
    Returns the discovered crafted modifiers for a player
    """

    # Retrieve player UUID
    player_uuid = player.get_uuid_from_username(username)

    # Guard clause
    if not player_uuid:
        return None

    # Initiate crafted modifiers dictionary
    crafted_modifiers: dict = {}

    # Retrieve available crafted modifiers
    crafted_modifiers_data = get_crafted_modifiers_data().get(player_uuid.replace('-', ''))

    # Loop through vault gear pieces
    for vault_gear in crafted_modifiers_data:

        # Initiate variables
        vault_gear_crafted_modifiers = []

        # Loop through crafted modifiers
        for crafted_modifier in crafted_modifiers_data.get(vault_gear).value:

            # Initiate variables
            crafted_modifier_id = crafted_modifier.value[:crafted_modifier.value.rfind('_')]
            crafted_modifier_tier = int(crafted_modifier.value[crafted_modifier.value.rfind('_') + 1:].replace('t', ''))

            # Initiate variables
            crafted_modifier_values = []

            # Read crafted modifiers config file
            with open(os.path.join('config', 'the_vault', 'gear_modifiers', f'{vault_gear.replace("the_vault:", "")}.json'), 'r') as f:
                
                # Retrieve config file data
                gear_modifier_config: dict = json.load(f)

                # Initiate variables
                crafted_modifier_positions = ['prefix', 'suffix']

                # Loop through crafted modifier positions
                for position in crafted_modifier_positions:
                    
                    # Guard clause
                    if f'CRAFTED_{position.upper()}' not in gear_modifier_config['modifierGroup'].keys():
                        continue

                    # Initiate variables
                    available_crafted_modifiers = gear_modifier_config['modifierGroup'].get(f'CRAFTED_{position.upper()}')

                    # Loop through available crafted modifiers
                    for available_crafted_modifier in available_crafted_modifiers:

                        # Guard clause
                        if available_crafted_modifier['identifier'] != crafted_modifier_id:
                            continue
                        
                        # Initiate variables
                        crafted_modifier_tier_data = available_crafted_modifier['tiers'][crafted_modifier_tier]

                        # Guard clause
                        if 'soulbound' in crafted_modifier_id:
                            crafted_modifier_values.append(1)
                            crafted_modifier_values.append(1)
                            break

                        # Initiate variables
                        crafted_modifier_value_min = crafted_modifier_tier_data['value']['min']
                        crafted_modifier_value_max = crafted_modifier_tier_data['value']['max']

                        # Format values
                        if crafted_modifier_value_min % 1 != 0 or crafted_modifier_value_max % 1 != 0:
                            crafted_modifier_value_min = f'{crafted_modifier_value_min * 100}%'
                            crafted_modifier_value_max = f'{crafted_modifier_value_max * 100}%'

                        crafted_modifier_values.append(crafted_modifier_value_min)
                        crafted_modifier_values.append(crafted_modifier_value_max)

                        # Break for loop
                        break

                    if len(crafted_modifier_values) != 0:
                        break
                    
            # Format variables
            crafted_modifier_id = format.format_id(
                crafted_modifier_id,
                [
                    {
                        'file_path': FILE_LANG,
                        'id_path': 'crafted_modifiers'
                    }
                ]
            )
            crafted_modifier_tier = crafted_modifier_tier + 1

            # Initiate crafted modifier data
            crafted_modifier_data: dict = {
                'id': crafted_modifier_id,
                'tier': crafted_modifier_tier,
                'values': crafted_modifier_values
            }

            # Add crafted modifier data to list
            vault_gear_crafted_modifiers.append(crafted_modifier_data)

        # Format vault gear
        vault_gear = format.format_id(format.preformat_id(vault_gear))

        # Add vault gear piece to dictionary
        crafted_modifiers[vault_gear] = vault_gear_crafted_modifiers
        

    # Return data
    return crafted_modifiers