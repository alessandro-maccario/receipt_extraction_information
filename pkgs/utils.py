"""
Utility module to store those functions that do not belong to a specific class
"""

import os
import re
from tqdm import tqdm


def folder_if_not_exist(folder_name):
    """Create folder if not exists"""
    # Check whether the specified path exists or not
    isExist = os.path.exists(folder_name)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(folder_name)
        tqdm.write("\nNew directory created..")


def path_normalizer(path):
    # normalize the path if there are backslash
    result_path = os.path.normpath(path)
    result_path = result_path.replace("\\", "/")

    return result_path


def regex_substitution(text):
    """
    Remove the space between digits in a string and substitute the "," with a "."
    """
    remove_spaces_between_numbers = re.compile(r"(\d+)\s*,\s*(\d+)")
    text_substitution = re.sub(remove_spaces_between_numbers, r" \1.\2 ", text)

    return text_substitution
