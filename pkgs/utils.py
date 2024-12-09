"""
Utility module to store those functions that do not belong to a specific class
"""

import csv
from datetime import datetime
import glob
import os
import re
from tqdm import tqdm
import sys

# This imports a helper tool, StringIO, that lets you treat a string as if it were a file.
from io import StringIO
import pandas as pd

# Add the root folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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
    ).strip()

    # Step 2: Extract date
    date_match = re.search(r"\b\d{2}[./]\d{2}[./]\d{4}\b", cleaned_date_text)
    # if date_match is not None (meaning a match was found), date will be set to the matched date string (e.g., "23.05.2021").
    date_group = date_match.group() if date_match else None
    # convert the date in the correct format
    date = datetime.strptime(date_group, "%d.%m.%Y").strftime("%Y.%m.%d")

    # Step 3: Extract items and prices
    # Find all items and prices by splitting and matching patterns
    items_and_prices = []
    for match in re.finditer(
        r"([a-zA-ZäöüÄÖÜß\s\-/]+)(?:\s+\d+%?)?,(-?\s*\d+\.\d{2})", cleaned_date_text
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
    df["price"] = df["price"].apply(lambda x: str(x).replace(" ", ""))

    return df


def md2csv(markdown_table):
    """Convert a markdown table to a pandas dataframe

    Parameters
    ----------
    markdown_table : str
        Markdown table containing the receipt data

    Returns
    -------
    pd.DataFrame
        Pandas dataframe with the data from the md string
    """
    lines = markdown_table.split("\n")

    # Use StringIO to create a file-like object from the string
    # markdown_table_io = io.StringIO(markdown_table)

    dict_reader = csv.DictReader(lines, delimiter="|")

    data = []
    # skip first row, i.e. the row between the header and data with only "---------------"
    for row in list(dict_reader)[1:]:
        # strip spaces and ignore first empty column
        try:
            r = {k.strip(): v.strip() for k, v in row.items() if k != ""}
            data.append(r)
        except AttributeError:
            r = ""
            data.append(r)

    return pd.DataFrame(data)


def date_convert(date_to_convert):
    return datetime.strptime(date_to_convert, "%d.%m.%Y").strftime("%Y.%m.%d")


def combine_csv(dir_path: str) -> None:
    """Concatenate and then convert to a final csv all the csvs containing data for date, item, price

    Parameters
    ----------
    dir_path : str
        The path where to find the csv data
    """
    # grab each file in each directory: when recursive is set, ** followed by a path separator matches 0 or more subdirectories.
    all_files = glob.glob(f"{dir_path}/*_cleaned.csv", recursive=False)

    csv_list = []

    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        csv_list.append(df)

    # concatenate all the csvs
    frame = pd.concat(csv_list, axis=0, ignore_index=True)
    # convert the date to Y.m.d format
    frame["date"] = frame["date"].apply(date_convert)

    # save the final pandas dataframe into a csv file
    frame.to_csv(f"{dir_path}/item_price_cleaned.csv", index=False)
