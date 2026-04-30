"""
This script is currently only a DRAFT
"""

import ollama
import base64
import json
from pathlib import Path


def extract_data_from_image_local(image_path, output_json="extracted_data.json"):
    """Extract data using a local model via Ollama"""

    # Read and encode the image
    with open(image_path, "rb") as image_file:
        image_data = base64.standard_b64encode(image_file.read()).decode("utf-8")

    # Create the prompt
    prompt = """Please analyze this image and extract all relevant data. 
    If it's a receipt, extract: store name, date, items, prices, city, and category.
    Return the data as a valid JSON object."""

    # Call local model (using LLaVA for vision capabilities)
    response = ollama.generate(
        model="llava",  # or 'neural-chat', 'mistral', etc.
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
