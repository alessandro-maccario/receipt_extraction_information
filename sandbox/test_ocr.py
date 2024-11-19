"""Reference:
- https://learnopencv.com/edge-detection-using-opencv/
- https://stackoverflow.com/questions/72528380/how-to-get-coordinates-of-the-overall-bounding-box-of-a-text-image
- https://github.com/JaidedAI/EasyOCR
- https://www.jaided.ai/easyocr/documentation/
"""

import sys
import os
import pytesseract


# Add the root folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sandbox.image_processing import ImageProcessing
from sandbox.text_extraction import TextExtraction
from sandbox.contour_finding import ContourFinding
from sandbox.deskewing import Deskewing

# define where tesseract lies
pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

# NOTE: not working correctly. Maybe use of EasyOCR:
# NOTE: https://github.com/JaidedAI/EasyOCR
# # image processing
# image_processing = ImageProcessing()
# search_contours = image_processing.topdown_view()

# # text extraction
# text_extraction = TextExtraction()
# content = text_extraction.extract_info()
# print(content)

genius_scan = "sandbox/receipts/genius_scan_1.jpg"
# orig = "sandbox/test_cut.jpg"

# to cut each contour into small images
contour_finding = ContourFinding(genius_scan)
search_contours = contour_finding.drawing_contours()

# to deskew the image and rotate it correclty to be front view
# deskewing = Deskewing(image_path=orig)
# orig_deskewing = deskewing.deskew()
