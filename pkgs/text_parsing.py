import os
import sys
import re
import glob
import pandas as pd
import spacy
from pathlib import Path
from symspellpy import SymSpell, Verbosity


# Add the root folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pkgs.text_contour_finding import (
    path_normalizer,
)
from pkgs.item_price_csv_dump import item_price_preprocess


# Load the Small German dictionary taken from Leipzig Corpora
nlp_sm = spacy.load("de_core_news_sm")

# path to the folder containing the text extracted from the images
text_extraction_dir = "sandbox/text_extraction"

# regex patterns
remove_spaces_between_numbers = re.compile(r"(\d+)\s*,\s*(\d+)")
date_matcher = r"(\d+\/\d+\/\d+)"
# (?:...) is a non-capturing group, meaning it groups things together without extracting them as separate matches.
# The ? at the end makes the entire group optional. This means that a number like 2 (no decimal part) will still match, but if there is a decimal, it must follow the [0-9]+ rules.
regx_pattern_item_price = r"([a-zA-ZäöüßÄÖÜéÉ ]+),\s*([0-9]+(?:[.,][0-9]+)?)"

# find the txt to be processed
text_extracted = glob.glob(f"{text_extraction_dir}/*.txt", recursive=False)
print("TEXT EXTRACTED:", text_extracted)


for txt_file in text_extracted:
    # grab only the txt name to be fed as a filename for saving the correct file
    txt_file_path_to_name = Path(txt_file)
    txt_filename = txt_file_path_to_name.name[:-4]

    txt_file = path_normalizer(txt_file)

    with open(txt_file) as txt_processing:
        # print the entire text
        # print("".join(txt_processing))
        txt_content = "".join(txt_processing)
        # print(txt_processing.readlines())  # list containing lines of file)

        text_substitution = re.sub(
            remove_spaces_between_numbers, r" \1.\2 ", txt_content
        )
        # print("Substituted text:", text_substitution)

        # date matcher
        date_finder = re.findall(date_matcher, text_substitution)
        # print("Date:", date_finder)

        # remove the forward slashes in the text (the date should have already been parsed!)
        text_substitution = text_substitution.replace("/", "")

        # based on the following regex, create a list of tuples that contains (item, price)
        item_price = re.findall(regx_pattern_item_price, text_substitution)
        # remove the " " element in the list
        item_price = [item_tuple for item_tuple in item_price if item_tuple[0] != " "]
        # remove elements if the price is not #.## but integer or a big number (30177616 for instance)
        item_price = [item_tuple for item_tuple in item_price if "." in item_tuple[1]]
        print("Test item, price:", item_price)

        # TODO: For each item in the tuple, get only the text, split it into token, check and edit the text if the token is found in the dictionry, write back the item to the tuple -> DONE by using the script Spacy/Symspell
        # NOTE: Here, you would need to implement the script that uses Spacy and Syspell. Need to move that script somewhere else in a class/method/function
        # NOTE: and call it here to be able to process the text and output the same [(item, price), (item, price), ...] list to then convert
        # NOTE: it to a DataFrame. In case then you want to apply specific rules (remove the "Netto", "Summe") and so on from the dataframe
        # NOTE: then you would need a filter to be applied depending on which receipt you are getting into. For instance, if it it a work related
        # NOTE: one, then you will process that in a different way than an Hofer/Spar/EuroSpar/Lidl one.

        ##############
        # NOTE: here add the function to preprocess and correct the list of item, prices before creating the saving the data to csv
        item_price_list_tuples = item_price_preprocess(
            nlp=nlp_sm, text_item_price=item_price
        )
        ##############

        # convert and save the pd.DataFrame into a csv
        df = pd.DataFrame(list(item_price_list_tuples), columns=["item", "price"])
        # print(df)
        df.to_csv(f"sandbox/text_extraction/{txt_filename}_result.csv", index=False)

# print([item[0] for item in item_price])
