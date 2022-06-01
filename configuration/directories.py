import os
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
SETTINGS_DIR = Path(__file__).resolve().parent  # settings dir
ROOT_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = os.path.join(ROOT_DIR, "logs")


def is_folder_exists(_dir: str) -> bool:
    if os.path.exists(_dir) and os.path.isdir(_dir):
        return True
    return False


def check_and_create_dir(dir_name: str, retrn_val: str = False):
    not_exists: bool = not is_folder_exists(dir_name)
    if not_exists:
        os.makedirs(dir_name)
        print("Directory <" + dir_name + "> created")

    if retrn_val:
        return not_exists


def create_neccessary_directories():
    directory_list = [
        LOGS_DIR,
    ]
    for _dir in directory_list:
        check_and_create_dir(_dir)
