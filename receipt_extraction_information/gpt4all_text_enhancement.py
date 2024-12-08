"""This script takes the .txt results from the EasyOCR extraction and fix/polish the
output to be correctly formatted before using it in the main .csv file.
"""

#######################
### IMPORT PACKAGES ###
#######################

import glob
from gpt4all import GPT4All
import os
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pkgs.utils import path_normalizer, md2csv
from pkgs.constants import LLAMA_32_3B_MODEL

#######################
######## MAIN #########
#######################

# path to the folder containing the text extracted from the images
text_extraction_dir = "sandbox/text_extraction"
# find the txt to be processed
text_extracted = glob.glob(f"{text_extraction_dir}/*_result.csv", recursive=False)

# chose the model to be used for polishing the data into a .csv format
MODEL_PATH = LLAMA_32_3B_MODEL

# call the model just once, not at every iteration
model = GPT4All(
    MODEL_PATH,
    device="cpu",
)

for csv_file in tqdm(text_extracted):
    # grab only the txt name to be fed as a filename for saving the correct file
    csv_file_path_to_name = Path(csv_file)
    csv_filename = csv_file_path_to_name.name[:-4]

    # normalize the backslash to forward slash
    csv_file = path_normalizer(csv_file)

    # Load the data
    df = pd.read_csv(csv_file)

    # Generate the markdown table
    df_md_conversion = df.to_markdown(index=False)

    # PROMPT WITH DATAFRAME IN MD
    PROMPT_RECEIPT_V3 = f"""
                        {df_md_conversion}
                        
                        It contains items and their prices. 
                        Correct any grammar/mispelling mistakes either from the German or the English language.
                        If no corrections are needed, leave the markdown untouched. 
                        ONLY accepted answer: the markdown table.
                        Do not infer any extra information from the text provided.
                        Translate the items to English, if they are not yet translated.
                        Stick only to the information provided. 
                        Column headers must be in small letters. 
                        Do not add any other comment to the answer, just the markdown.
                        Do not add any other text such as "Here is the corrected CSV:".
                        Remove any rows that is not related to an shopping item.
                        """

    # feed the model with the prompt and generate response
    with model.chat_session():
        response = model.generate(PROMPT_RECEIPT_V3)
        content = model.current_chat_session

    # extract the content if the role is assistant that matches the answer from the model
    for json_dict in content:
        if json_dict["role"] == "assistant":
            md_item_price_table = "".join(json_dict["content"])

    # convert the markdown output into a csv table
    markdown_to_csv_conversion = md2csv(md_item_price_table)
    # print(markdown_to_csv_conversion)

    # save the md2csv into a csv file
    markdown_to_csv_conversion.to_csv(
        f"sandbox/text_extraction/{csv_filename}_cleaned.csv", index=False
    )
