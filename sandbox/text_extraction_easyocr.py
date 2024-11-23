"""
Testing extraction from receipt images by using EasyOCR:
- https://github.com/JaidedAI/EasyOCR
- https://www.jaided.ai/easyocr/
- https://www.jaided.ai/easyocr/documentation/

Script already used in the image_processing.py file in the pkgs folder!

"""

import easyocr
import time

original_path = "sandbox/receipts/original.jpg"
genius_scan = "sandbox/receipts/genius_scan_1.jpg"
roi_path = "sandbox/receipts/test_roi/cut_roi_7.jpg"

# start counting the time needed for the script to run
start_time = time.time()

# this needs to run only once to load the model into memory
reader = easyocr.Reader(["de", "en"], gpu=False)
result = reader.readtext(roi_path, detail=0)
result_string = ",".join(result)

with open("sandbox/text_extraction/text_extraction_cut_roi7.txt", "w") as f:
    f.write(result_string)

print(print("--- %s seconds ---" % (time.time() - start_time)))
