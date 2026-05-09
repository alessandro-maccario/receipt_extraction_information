"""
This script is currently only a DRAFT
"""

import ollama
import base64
import json
from pathlib import Path


def extract_data_from_image_local(
    image_path, output_json="/home/m/Documents/expenses_data/extracted_data.json"
):
    """Extract data using a local model via Ollama"""

    # Read and encode the image
    with open(image_path, "rb") as image_file:
        image_data = base64.standard_b64encode(image_file.read()).decode("utf-8")

    # Create the prompt
    prompt = """This is a picture of a receipt that could be in German or Italian language.

                Please, extract all relevant information such as:
                - date (format the time as: YYYY/MM/DD)
                - expense_category
                - item (item name)
                - value (price per item in euro)
                - store
                - city
                - category

                Where the expense_category that you can use are as follows:
                - Apparel
                - Dining and Restaurants
                - Education and Learning
                - Entertainment and Leisure
                - Food and Groceries
                - Fuel
                - Home and Living
                - Household and Personal Care
                - Miscellaneous
                - Transportation
                - Travel

                And the category can be one of the following (only food related):
                - Alcoholic Beverages
                - Cereal and Bakery Products
                - Dairy Products
                - Fish and Seafood
                - Fruits and Vegetables
                - Meat and Meat Products
                - Non-Alcoholic Beverages
                - Sugars and Confectionery

                Sometimes, if multiple items are bought in the same receipt, you will see a number multiplied by the item price. You will separate these multiple entries in different JSON records.
                Please, provide the results in a JSON format.
                No tax details, transaction or total amount information is needed, but only the data that I've specified.
                Do not add any additional text to your output: stick only with the JSON output format of the receipt."""

    # Call local model (using LLaVA for vision capabilities)
    response = ollama.generate(
        model="Qwen2.5VL:3b",
        prompt=prompt,
        images=[image_path],
        stream=False,
    )

    response_text = response["response"]

    # Parse JSON from response
    try:
        import re

        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            extracted_data = json.loads(json_match.group())
        else:
            extracted_data = {"raw_response": response_text}
    except json.JSONDecodeError:
        extracted_data = {"raw_response": response_text}

    # Save to JSON file
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False)

    print(f"Data extracted and saved to {output_json}")
    return extracted_data


# Usage
extract_data_from_image_local("receipt.jpg", "receipt_data.json")
