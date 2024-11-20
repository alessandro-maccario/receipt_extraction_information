"""This script takes the .txt results from the EasyOCR extraction and fix/polish the
output to be correctly formatted before using it in the main .csv file.
"""

# define a prompt to be fed into GPT4All.
PROMPT = ""

# chose the model to be used for polishing the data into a .csv format
MODEL = "Phi-3 Mini Instruct"
