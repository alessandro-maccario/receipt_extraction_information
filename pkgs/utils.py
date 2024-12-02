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


def merge_bounding_boxes(bounding_boxes, threshold=10):
    """
    Merge overlapping or close enough bounding boxes based on the threshold parameter.

    Args:
        bounding_boxes: List of bounding boxes (x, y, w, h).
        threshold: Maximum distance between boxes to consider merging.

    Returns:
        List of merged bounding boxes.
    """
    merged_boxes = []

    for box in bounding_boxes:
        x, y, w, h = box
        merged = False
        for mbox in merged_boxes:
            mx, my, mw, mh = mbox
            # Check if the boxes are close enough to merge
            if (
                x < mx + mw + threshold
                and mx < x + w + threshold
                and y < my + mh + threshold
                and my < y + h + threshold
            ):
                # Merge the boxes by extending boundaries
                mbox[0] = min(mx, x)
                mbox[1] = min(my, y)
                mbox[2] = max(mx + mw, x + w) - mbox[0]
                mbox[3] = max(my + mh, y + h) - mbox[1]
                merged = True
                break

        if not merged:
            merged_boxes.append([x, y, w, h])

    return merged_boxes
