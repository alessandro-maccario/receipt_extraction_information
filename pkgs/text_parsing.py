import os
import sys
import re
import glob
import pandas as pd
import spacy
from symspellpy import SymSpell, Verbosity


# Add the root folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pkgs.text_contour_finding import (
    path_normalizer,
)

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

        # # convert and save the pd.DataFrame into a csv
        # df = pd.DataFrame(list(test_item_price), columns=["item", "price"])
        # print(df)
        # df.to_csv("sandbox/text_extraction/result_original.csv", index=False)

print([item[0] for item in item_price])


###################################
# Spacy and Syspell for tokenization and spelling correction
# download small model
# !python -m spacy download de_core_news_sm

# Load German dictionary taken from Leipzig Corpora
nlp_sm = spacy.load("de_core_news_sm")

# instantiate SymSpell obkect
sym_spell = SymSpell(max_dictionary_edit_distance=2)
# load SymSpell German dictionary
sym_spell.load_dictionary(
    "data/de_polished.txt", term_index=0, count_index=1, encoding="utf-8"
)

# test if the algorithm works
text_input = [
    ("X Glas Masser Ieer", "0.00"),
    ("Salat groß", "2.40"),
    (" Metto", "2.10"),
    ("Sumne", "2.40"),
]
print("\n")

# Reference: https://github.com/wolfgarbe/SymSpell

# create a list to store the fixed (item, price) tuple
fixed_item_price_list = []

for text_item_tup in text_input:
    # create a list to store the corrected item and price
    text_input_corrected = []
    # grab only the text of the tuple
    clean_text = text_item_tup[0].strip()
    # grab only the price of the tuple
    item_price = text_item_tup[1]

    # process the all text of the tuple
    doc = nlp_sm(clean_text)
    print("\nToken:", doc)

    # Tokenization
    # print("Tokens:", [token.text for token in doc])

    for token in doc:
        # Test word
        input_word = token.text
        suggestions = sym_spell.lookup(input_word, Verbosity.TOP, max_edit_distance=2)

        # Print suggestions
        if suggestions:
            for suggestion in suggestions:
                # print("Correct Token:", suggestion.term)
                # new_token_list.append(suggestion.term)

                # substitute the text with the new correct string
                text = "".join(suggestion.term)
                # print("\nCorrected text:", text)

                # append to list and join each string word
                text_input_corrected.append(text)
                text_input_corrected_joined = " ".join(text_input_corrected)

                break
                # print(f"Suggestion: {suggestion.term}, Distance: {suggestion.distance}, Frequency: {suggestion.count}")
        else:
            print("No suggestions found.")

    # save the corrected text and the price in a tuple
    fixed_item_price_list.append((text_input_corrected_joined, item_price))


print(text_input_corrected_joined)
print(fixed_item_price_list)
