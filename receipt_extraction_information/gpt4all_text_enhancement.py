"""This script takes the .txt results from the EasyOCR extraction and fix/polish the
output to be correctly formatted before using it in the main .csv file.
"""

import glob
from gpt4all import GPT4All
import os
import pandas as pd
from pathlib import Path
import pprint
import time
from tqdm import tqdm
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pkgs.utils import path_normalizer, md2csv


# path to the folder containing the text extracted from the images
text_extraction_dir = "sandbox/text_extraction"
# find the txt to be processed
text_extracted = glob.glob(f"{text_extraction_dir}/*_result.csv", recursive=False)

# chose the model to be used for polishing the data into a .csv format
MODEL_PATH = os.path.abspath("model/Llama-3.2-3B-Instruct-Q4_0")

# define a prompt to be fed into GPT4All.
# PROMPT_RECEIPT_V1 = """Extract the following receipt text into this markdown CSV format:
#                     date, item, price. Keep discounts (e.g., App-Joker), but remove unnecessary information such like Sum/Summe.
#                     Please, it is not allowed to have any other text unless the requested CSV dataframe.
#                     Text: 'Ihr Einkauf,am  28.11  . 2024,Uni,14.29 Uhr,EUR,SPAR HALF BAKED ICE, 4.99 ,App-Joker   25%,- 1.25 , pasta barilla, 1.20 , SUMME 4.94'.
#                  """
# PROMPT_RECEIPT_V2 = """
#                     Task: take a text from a supermarket/restaurant receipt, sometimes in German, sometimes in English and
#                     return a csv like file format with the following structure: date, item, price.
#                     Remove any unnecessary information (Remove any Sum or any other translations or mispelled variations of it.
#                     I do need to keep discount information such as 'App-Joker' on a new line).
#                     Just answer to this request by giving the requested CSV dataframe, you are prohibited to add any other text to it.
#                     Here is the text: 'Ihre Ersparnis:  1.25  EUR Ihr Einkauf,am  28.11  . 2024,Uni,14.29 Uhr,EUR,SPAR HALF BAKED ICE, 4.99 ,App-Joker   25%,- 1.25 ,SUHME, 3.74 Villacherstrale 1/ 1.9020  Klagenfur t,Tel, 0463.210229 EUROSPAR'.
#                     """

# call the model just once, not at every iteration
model = GPT4All(
    MODEL_PATH,
    device="cpu",
)

for csv_file in tqdm(text_extracted):
    # grab only the txt name to be fed as a filename for saving the correct file
    csv_file_path_to_name = Path(csv_file)
    csv_filename = csv_file_path_to_name.name[:-4]

    csv_file = path_normalizer(csv_file)
    # print("\nCSV FILE:", csv_file, "\n")

    # TODO: TEST WITH ONE CSV: READ THE CSV CREATED BY THE text_parsing.py SCRIPT AND CONVERT IT TO MD BEFORE FEEDING IT INTO GPT4ALL
    # Load the data
    df = pd.read_csv(csv_file)

    # Generate the markdown table
    df_md_conversion = df.to_markdown(index=False)

    # PROMPT WITH DATAFRAME IN MD
    PROMPT_RECEIPT_V3 = f"""
                        {df_md_conversion}
                        
                        It contains items and their prices. 
                        Correct any grammar/mispelling mistakes either from the German or the English language. 
                        Only accepted answer: the markdown table.
                        Do not infer any extra information from the text provided.
                        Stick only to the information provided. 
                        Column headers must be in small letters. 
                        If no corrections are needed, leave the markdown untouched. 
                        Do not add any other comment to the answer, just the markdown.
                        Do not add any other text such as "Here is the corrected CSV:".
                        Remove any rows that is not related to an shopping item.
                        """

    # # start counting the time needed for the model to be loaded
    # start_time = time.time()

    with model.chat_session():
        response = model.generate(PROMPT_RECEIPT_V3)
        # print(response)
        # pprint.pprint(model.current_chat_session)
        content = model.current_chat_session

    # extract the content if the role is assistant that matches the answer from the model
    for json_dict in content:
        if json_dict["role"] == "assistant":
            md_item_price_table = "".join(json_dict["content"])
            # print(json_dict["content"])

    # TODO: need to convert this markdown file to a JSON and then to a csv format like

    # convert the markdown output into a csv table
    markdown_to_csv_conversion = md2csv(md_item_price_table)
    # print(markdown_to_csv_conversion)

    # save the md2csv into a csv file
    markdown_to_csv_conversion.to_csv(
        f"sandbox/text_extraction/{csv_filename}_cleaned.csv", index=False
    )

    # print("--- %s seconds ---" % (time.time() - start_time), "\n")
