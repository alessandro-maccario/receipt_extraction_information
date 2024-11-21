"""This script applies image processing techniques in order to preprocess the image
before feeding it into EasyOCR.

Reference:
- https://learnopencv.com/edge-detection-using-opencv/
- https://stackoverflow.com/questions/72528380/how-to-get-coordinates-of-the-overall-bounding-box-of-a-text-image
- https://github.com/JaidedAI/EasyOCR
- https://www.jaided.ai/easyocr/documentation/
"""

import os
import sys
import pytesseract

# Add the root folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pkgs.text_contour_finding import ContourFinding
from pkgs.image_polishing import ImageProcessing


# path to the image
# orig = "sandbox/test_cut.jpg"
genius_scan = "sandbox/receipts/input/genius_scan.jpg"

# path to the folder containing the original images
# TODO: # 1. define the folder path
src_dir = "sandbox/receipts/input"
roi_dir = "sandobox/receipts/output_roi"


# TODO: # 2. loop through the images, cut them (using the image_polishing.py file that cut the entire image)
# TODO: and save them in output_cut folder

# for image in os.listdir(src_dir):
#     # check if the image ends with png
#     if image.endswith(".jpg"):
#         # create the full path to feed it into the contour_finding
#         src_image = f"{src_dir}/{image}"

#         # TODO: # 3. To this images, apply the text_contour_finding.py to cut them in small pieces based on text and save the pieces in each individual folder in output_cut/image_cut_1/
#         # cut each text contour into small images to be fed into EasyOCR
#         contour_finding = ContourFinding(src_image)
#         search_contours = contour_finding.cut_bounding_box()


# TODO: # 4. Loop through the directories of the cut images and apply EasyOCR to save the text extracted
# the search of the folder name does not work. It works if you use "."
for root, dirs, files in os.walk(".", topdown=False):
    for name in dirs:
        print(name)

# TODO: # 5. Loop through each text file using regex to keep only item/price
# TODO: # 6. feed this final file to Phi3 with the same prompt to rearrange it correctly and save it to a .csv file to be used


# image_processing = ImageProcessing()
# topdown_view = image_processing.topdown_view()
