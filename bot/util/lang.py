import os
from sys import platform

from main import TESTING


if platform != "win32":
    if TESTING == False:
        VAULT_LANG_PATH: str = os.path.join("eternal-smp-bot", "lang", "the_vault.json")
        OTHER_PATH: str = os.path.join("eternal-smp-bot", "lang", "other.json")
    else:
        VAULT_LANG_PATH: str = os.path.join("test-eternal-smp-bot", "lang", "the_vault.json")
        OTHER_PATH: str = os.path.join("test-eternal-smp-bot", "lang", "other.json")

else:
    VAULT_LANG_PATH: str = os.path.join("lang", "the_vault.json")
    OTHER_PATH: str = os.path.join("lang", "other.json")
