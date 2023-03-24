# Other imports
import os

def get_config_file(path: str):
    """
    Returns the config file for a specific path
    """

    # Retrieve the_vault config folder
    config_file = os.path.join('config', 'the_vault')

    # Retrieve config file
    for path_segment in path.split('.'):
        config_file = os.path.join(config_file, path_segment)

    # Return config file
    return config_file