"""
Using an LLM, extract the data from a receipt and output the results as JSON.
Convert all the JSON into an .ods file.
"""

import json
import os
import pandas as pd

json_directory = "/home/m/Documents/expenses_data/json_receipts/"
all_data = []

for filename in os.listdir(json_directory):
    if filename.endswith(".json"):
        # create fullpath such as: /home/m/Documents/expenses_data/json_receipts/20260421_222502.json
        filepath = os.path.join(json_directory, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            # checks if the JSON data is a list and adds all its elements to a collection
            if isinstance(data, list):
                all_data.extend(data)

# Convert to DataFrame and save as ODS
df = pd.DataFrame(all_data)

# Save data to odf
df.to_excel(
    "/home/m/solutions/learning_python/receipt_extraction_information/output/output.ods",
    sheet_name="Data",
    index=False,
    engine="odf",
)

print("ODS file created successfully!")
