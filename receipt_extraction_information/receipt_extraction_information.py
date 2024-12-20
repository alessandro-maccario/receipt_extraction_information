"""
This script applies image processing techniques in order to preprocess the image
before feeding it into EasyOCR.

Reference:
- https://learnopencv.com/edge-detection-using-opencv/
- https://stackoverflow.com/questions/72528380/how-to-get-coordinates-of-the-overall-bounding-box-of-a-text-image
- https://github.com/JaidedAI/EasyOCR
- https://www.jaided.ai/easyocr/documentation/

Testing extraction from receipt images by using EasyOCR:
- https://github.com/JaidedAI/EasyOCR
- https://www.jaided.ai/easyocr/
- https://www.jaided.ai/easyocr/documentation/

Symspell:
- Leipzig Corpora: https://corpora.uni-leipzig.de/en?corpusId=deu_news_2023
"""

#######################
### IMPORT PACKAGES ###
#######################

import easyocr
import glob
import logging
import os
import re
from pathlib import Path
import subprocess
import sys
import time
from tqdm import tqdm


# Add the root folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pkgs.text_contour_finding import ContourFinding
from pkgs.utils import (
    folder_if_not_exist,
    path_normalizer,
    regex_substitution,
    combine_csv,
)

#######################
######## MAIN #########
#######################

# instantiate the logger to be able to save logs information, INFO level
logger = logging.getLogger(__name__)
logging.basicConfig(filename="info.log", encoding="utf-8", level=logging.INFO)

# path to the folder containing the original images
# 1. define the folder path
src_dir = "sandbox/receipts/input"
roi_dir = "sandbox/receipts/output_roi"


# 2. loop through the images, cut them (using the image_polishing.py file that cut the entire image) and save them in output_cut folder
def main():
    for image in os.listdir(src_dir):
        # check if the image ends with png
        if image.endswith(".jpg"):
            # create the full path to feed it into the contour_finding
            src_image = f"{src_dir}/{image}"

            # 3. To this images, apply the text_contour_finding.py to cut them in small pieces based on text and save the pieces in each individual folder in output_cut/image_cut_1/
            # cut each text contour into small images to be fed into EasyOCR
            contour_finding = ContourFinding(src_image)
            search_contours = contour_finding.cut_bounding_box()

    # 4. Loop through the directories of the cut images and apply EasyOCR to save the text extracted
    # grab each file in each directory: when recursive is set, ** followed by a path separator matches 0 or more subdirectories.
    roi_images = glob.glob(f"{roi_dir}/**/*.jpg", recursive=True)
    # print(roi_images)

    # start counting the time needed for the model to be loaded
    start_time = time.time()
    # this needs to run only once to load the model into memory
    reader = easyocr.Reader(["de", "en"], gpu=False)
    print("--- %s seconds ---" % (time.time() - start_time), "\n")

    # add a progress bar to the operation
    for image_path in tqdm(roi_images, position=0, leave=True):
        # normalize the path if there are backslash
        image_path = path_normalizer(image_path)
        # save logging information into a file
        logger.info(f"Image path: {image_path}")

        # grab only the image name to be fed as a filename for the roi and the cut
        image_path_to_name = Path(image_path)
        image_name = image_path_to_name.name
        # grab only the basename of the file, without any additional information about the roi
        image_basename = re.sub(r"(_roi_\d+.jpg)", "", image_name)

        # no details: just the bare text extracted
        result = reader.readtext(image_path, detail=0)
        result_string = ",".join(result)
        # apply regex substitution to substitute the spaces between digits and the comma with a dot
        result_string = regex_substitution(result_string)
        # print(result_string)

        # if the folder for the specific image does not exits, create one
        folder_if_not_exist(f"sandbox/text_extraction/{image_basename}")

        with open(
            f"sandbox/text_extraction/{image_basename}/{image_name[:-4]}.txt", "w"
        ) as f:
            f.write(result_string)

    # 5. Loop through each text file using regex to keep only item/price
    # This would be taken care of by text_combiner.py to combine all the .txt files and then calling the text_parsing.py to tokenization and spell checking.
    subprocess.call([sys.executable, "receipt_extraction_information/txt_combiner.py"])
    subprocess.call([sys.executable, "receipt_extraction_information/text_parsing.py"])
    # 6. from the final csv files, create a script that, based on the store of the receipt
    # can automatically remove incorrect values (such as "Summe", "Netto") and so on.
    subprocess.call(
        [sys.executable, "receipt_extraction_information/gpt4all_text_enhancement.py"]
    )

    # 7. Merge all the csv into one
    # define the path where to find the csvs
    csv_dir = "sandbox/text_extraction"
    combine_csv(csv_dir)


if __name__ == "__main__":
    main()
