"""This script takes the .txt results from the EasyOCR extraction and fix/polish the
output to be correctly formatted before using it in the main .csv file.
"""

from gpt4all import GPT4All
import os
import pprint
import time

# define a prompt to be fed into GPT4All.
PROMPT_RECEIPT_V1 = """Extract the following receipt text into this markdown CSV format: 
                    date, item, price. Keep discounts (e.g., App-Joker), but remove unnecessary information such like Sum/Summe.
                    Please, it is not allowed to have any other text unless the requested CSV dataframe. 
                    Text: 'Ihr Einkauf,am  28.11  . 2024,Uni,14.29 Uhr,EUR,SPAR HALF BAKED ICE, 4.99 ,App-Joker   25%,- 1.25 , pasta barilla, 1.20 , SUMME 4.94'.
                 """
PROMPT_RECEIPT_V2 = """
                    Task: take a text from a supermarket/restaurant receipt, sometimes in German, sometimes in English and
                    return a csv like file format with the following structure: date, item, price. 
                    Remove any unnecessary information (Remove any Sum or any other translations or mispelled variations of it. 
                    I do need to keep discount information such as 'App-Joker' on a new line). 
                    Just answer to this request by giving the requested CSV dataframe, you are prohibited to add any other text to it. 
                    Here is the text: 'Ihre Ersparnis:  1.25  EUR Ihr Einkauf,am  28.11  . 2024,Uni,14.29 Uhr,EUR,SPAR HALF BAKED ICE, 4.99 ,App-Joker   25%,- 1.25 ,SUHME, 3.74 Villacherstrale 1/ 1.9020  Klagenfur t,Tel, 0463.210229 EUROSPAR'.
                    """

# chose the model to be used for polishing the data into a .csv format
MODEL_PATH = os.path.abspath("model/Meta-Llama-3-8B-Instruct.Q4_0")


# start counting the time needed for the model to be loaded
start_time = time.time()

# call the model
model = GPT4All(
    MODEL_PATH,
    device="cpu",
)
with model.chat_session():
    response = model.generate(PROMPT_RECEIPT_V2)
    print(response)
    pprint.pprint(model.current_chat_session)
    content = model.current_chat_session

print("--- %s seconds ---" % (time.time() - start_time), "\n")
