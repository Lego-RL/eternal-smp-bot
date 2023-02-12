# Project imports
import json

from backend_data import VAULT_LANG_PATH, OTHER_PATH



def format_id(object_id: str, alternate_files: list = []) -> str:
    """
    Return the name of an object's id based on given paths

    Parameters
    ----------
    item_id : str
        The id of the object to return the name of
    alternate_files: list(dict(str, str)) (optional)
        A list of files, containing: 'file_path', 'id_path' and 'name_path' as keys.
        'file_path': str
            The path the file is located in
        'id_path': str
            The path the id is located in within the file
        'name_path': str (optional)
            The path the name corresponding to the id is located in within the file
    """

    # Loop through alternate files
    for file in alternate_files:

        # Retrieve variables
        file_path = file.get("file_path")
        id_path = file.get("id_path")
        name_path = file.get("name_path") if file.get("name_path") != None else id_path

        with open(file_path, "r") as f:

            data: dict = json.load(f)

            # Retrieve id from id path
            data_id_path = data
            for path_child in id_path.split("."):
                data_id_path = data_id_path[(path_child)] #type: ignore
            
            # Retrieve name from name path
            data_name_path = data
            if name_path == id_path:
                if object_id in data_id_path.keys():
                    return data_id_path.get(object_id)
            else:
                for path_child in name_path.split(".")[:-1]:
                    data_name_path = data_name_path[(path_child)]
                if object_id in data_name_path.keys():
                    return data_name_path.get(name_path.split(".")[-1])

    # Retrieve default paths
    default_files = [
        VAULT_LANG_PATH,
        OTHER_PATH
    ]

    # Loop through default files
    for file in default_files:

        with open(file, "r") as f:

            data: dict = json.load(f)

            # Check if id is listed
            for key in data.keys():
                if object_id in key:
                    return data.get(object_id) #type: ignore

    # Return id (default)
    return object_id