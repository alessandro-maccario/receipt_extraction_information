import re
import pandas as pd


def regex_substitution(text):
    """
    Remove the spaces between digits in a string and substitute the "," with a "."
    """
    remove_spaces_between_numbers = re.compile(r"(\d+)\s*,\s*(\d+)")
    text_substitution = re.sub(remove_spaces_between_numbers, r" \1.\2 ", text)

    return text_substitution


example = "U,UU,Glas Wasser / Ieer,X Glas Masser /Ieer,0,00,Salat groß,2 , 40 Datum :,12/11/2024"
example_2 = """
Jennite
U,UU,Glas Wasser / Ieer,X Glas Masser /Ieer,0,00,Salat groß,2 , 40
Datum :,12/11/2024,Vihkainfineon77,KundenNr ,30177616,Bon-Nr ,,880338
Siemensstrale,9500,Vilach
Inf ineon Technofogves
Dussmann,Austria,GmbH
RKSV-Resse-Hr : %iKO,Kasse,VIHKAINFINEON
Herzlichen Dank Tür  Ihren Besuch
ATu 23260209
204,0,09 Netto 208,0,00 llust. 203
40 Metto,2, 10 Hust.705
omnabbuchuna,4u
Sumne,2 ,40

"""

remove_spaces_between_numbers = re.compile(r"(\d+)\s*,\s*(\d+)")

text_substitution = re.sub(remove_spaces_between_numbers, r" \1.\2 ", example_2)
print("Substituted text:", text_substitution)


# date matcher
date_matcher = r"(\d+\/\d+\/\d+)"
date_finder = re.findall(date_matcher, text_substitution)
print("Date:", date_finder)


# remove the forward slashes in the text (the date should have already been parsed!)
text_substitution = text_substitution.replace("/", "")

# based on the following regex, create a list of tuples that contains (item, price)
# (?:...) is a non-capturing group, meaning it groups things together without extracting them as separate matches.
# The ? at the end makes the entire group optional. This means that a number like 2 (no decimal part) will still match, but if there is a decimal, it must follow the [0-9]+ rules.
regx_pattern_item_price = r"([a-zA-ZäöüßÄÖÜéÉ ]+),\s*([0-9]+(?:[.,][0-9]+)?)"
test_item_price = re.findall(regx_pattern_item_price, text_substitution)
print("Test item, price:", test_item_price)


print("DF:\n", pd.DataFrame(list(test_item_price), columns=["item", "price"]))
