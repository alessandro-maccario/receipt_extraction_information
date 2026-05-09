from ollama import chat
import os
import json
import time
import pandas as pd

# Constants
image_folder_path = "/home/m/Documents/expenses_data/receipts/test_receipt/"
ollama_model = "minicpm-v:latest"

# 1st Phase: prompt the model with the image
start_time = time.time()

# Read the prompt in and pass it to the model
with open("prompt.txt") as fp:
    contents = fp.read()

# read all images in the folder
for filename in os.listdir(image_folder_path):
    if filename.lower().endswith((".jpg", "jpeg")):
        file_path = os.path.join(image_folder_path, filename)

        # Send single image to the model
        response = chat(
            model=ollama_model,
            messages=[
                {
                    "role": "user",
                    "content": f"""{contents}""",
                    "images": [file_path],
                }
            ],
        )

    # print(response["message"]["content"])

    # save the corresponding file with filename the name of the image
    with open(
        f"data/output/{filename.rsplit('.', 1)[0]}.json", "w"
    ) as json_content_receipt:
        json.dump(response["message"]["content"], json_content_receipt)

print("Read all the images and saved the content to JSON! ✅")
print("--- %s seconds ---" % (time.time() - start_time))

# 2nd Phase: save all the json receipts into an .odf file
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
