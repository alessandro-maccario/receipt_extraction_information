"""Once the image has been already processed
to get a Top-Down view of the receipt, then
apply PyTesseract to extract the information from
"""

import re
import cv2
import pytesseract


class TextExtraction:
    def __init__(self) -> None:
        self.image_path = "sandbox/genius_scan/genius_scan_2.jpg"

    # Step 2: Extract text using Tesseract
    def extract_text(self):
        # Step 1: Load the image
        image_top_down_view = cv2.imread(self.image_path)
        # Convert image to string
        config = "--psm 6"  # 6 = Assume receipt has uniform blocks of text; 3 for fully automatic, 11 for sparse text
        text = pytesseract.image_to_string(
            image_top_down_view, config=config, lang="de+eng"
        )  # use English and German
        return text

    # Step 3: Extract specific information
    def extract_info(self):
        text = self.extract_text()
        # print("TEXT IS:\n", text, "\n")
        item_extraction = re.findall(
            r"^(\d+)\s*x\s*([a-zA-Z \/]+)*(\d+,\d+)$", text, flags=re.MULTILINE
        )
        # extract item description and item_price from the text
        item = [(item[1].strip(), item[2]) for item in item_extraction]

        # Regex for finding the total (e.g., "Total: 12.34")
        total_match = re.search(r"(?i)Summe[:\s]*([\d.,]+)", text)
        total = total_match.group(1) if total_match else "Not Found"

        # Regex for finding the date (e.g., "15/11/2024" or "2024-11-15")
        date_match = re.search(r"(\d{2}[/-]\d{2}[/-]\d{4})", text)
        date = date_match.group(1) if date_match else "Not Found"

        return {"Date": date, "Total": total, "Item(s)": item}
