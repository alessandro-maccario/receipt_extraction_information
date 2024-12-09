"""
This script takes the extracted .txt file and extract only the most relevant information (such as
item, prices). Errors, mispelling and mistakes from the OCR extraction can still be present.

The script output, for each .txt file, a fixed version of it.

"""

#######################
### IMPORT PACKAGES ###
#######################

import os
import sys
import glob

# import spacy
from pathlib import Path

# Add the root folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pkgs.utils import path_normalizer, clean_receipt_text

#######################
######## MAIN #########
#######################

# path to the folder containing the text extracted from the images
text_extraction_dir = "sandbox/text_extraction"

# find the txt to be processed
text_extracted = glob.glob(f"{text_extraction_dir}/*.txt", recursive=False)

for txt_file in text_extracted:
    # grab only the txt name to be fed as a filename for saving the correct file
    txt_file_path_to_name = Path(txt_file)
    txt_filename = txt_file_path_to_name.name[:-4]

    txt_file = path_normalizer(txt_file)

    with open(txt_file) as txt_processing:
        # print the entire text
        txt_content = "".join(txt_processing)
        # remove unwanted text, clean the date, clean the prices
        df_cleaned_content = clean_receipt_text(txt_content)

        # save the cleaned data to csv
        df_cleaned_content.to_csv(
            f"sandbox/text_extraction/{txt_filename}_result.csv", index=False
        )
