"""
Utility module to store those functions that do not belong to a specific class
"""

import os
import re
from tqdm import tqdm
import sys

# This imports a helper tool, StringIO, that lets you treat a string as if it were a file.
from io import StringIO
import pandas as pd


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


def merge_bounding_boxes(bounding_boxes, threshold=15):
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


def clean_receipt_text(receipt_text):
    """Clean the text extracted from the receipt and converting it into a dataframe.

    Parameters
    ----------
    receipt_text : string
        Text extracted from the receipt in a string format.

    Returns
    -------
    pd.DataFrame
        Dataframe of the data in a csv format with date, item, price
    """
    # Step 1: Normalize spaces and remove irrelevant lines
    cleaned_text = re.sub(r"\s+", " ", receipt_text)  # Normalize spaces
    cleaned_text = re.sub(
        r"(Ihre Ersparnis:.*?|Tel.*?|EUROSPAR|Ihr Einkauf,am|SUHME|SUMME|SUMNE|Uhr|EUR|%|Uni)",
        "",
        cleaned_text,
    )  # Remove non-essential lines
    cleaned_date_text = re.sub(
        r"\s*(\d{2})\s*[./]\s*(\d{2})\s*[./]\s*(\d{4})", r" \1.\2.\3", cleaned_text
    )
    cleaned_date_text = re.sub(
        r"\s*(\d{2})\s*[./]\s*(\d{2})\s*[./]\s*(\d{4})", r" \1.\2.\3", cleaned_text
    ).strip()

    # Step 2: Extract date
    date_match = re.search(r"\b\d{2}\.\d{2}\.\d{4}\b", cleaned_date_text)
    date = date_match.group() if date_match else None

    # Step 3: Extract items and prices
    # Find all items and prices by splitting and matching patterns
    items_and_prices = []
    for match in re.finditer(
        r"([a-zA-Z\s\-]+)(?:\s+\d+%?)?,(-?\s*\d+\.\d{2})", cleaned_date_text
    ):
        item = match.group(1).strip()
        price = match.group(2).strip() if match.group(2) else None
        items_and_prices.append((item, price))

    # Step 4: Format as CSV-like structure
    csv_output = "date,item,price\n"
    for item, price in items_and_prices:
        csv_output += f"{date},{item},{price}\n"

    # Step 5: convert to dataframe
    df = pd.read_csv(StringIO(csv_output), sep=",")

    # Step 6: replace any spaces present in the price column, if any
    df["price"] = df["price"].apply(lambda x: x.replace(" ", ""))

    return df
