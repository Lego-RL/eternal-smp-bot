# Other imports
import python_nbt.nbt as nbt


def read_nbt(file_path: str) -> any:
    return nbt.read_from_nbt_file(file_path)