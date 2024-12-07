"""The txt_combiner reads in all the .txt files and combine them in one single file."""

#######################
### IMPORT PACKAGES ###
#######################
import os
import sys
import glob
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pkgs.utils import path_normalizer

#######################
######## MAIN #########
#######################

txt_dir = "sandbox/text_extraction"
# grab each file in each directory: when recursive is set, ** followed by a path separator matches 0 or more subdirectories.
txt_folder = glob.glob(f"{txt_dir}/*", recursive=False)
# print(txt_folder)

for each_folder in txt_folder:
    each_folder = path_normalizer(each_folder)
    # grab all the filename of the specific folder where the txts are stored
    filenames = glob.glob(f"{each_folder}/*", recursive=True)

    # grab only the folder name to be fed as a filename for the final entire txt file
    folder_path_to_name = Path(each_folder)
    folder_name = folder_path_to_name.name

    with open(f"{txt_dir}/result_{folder_name}.txt", "wb") as outfile:
        for f in filenames:
            with open(f, "rb") as infile:
                # about the \n encoding in ascii: https://stackoverflow.com/questions/21916888/cant-concat-bytes-to-str-when-using-subprocess-check-output
                outfile.write(infile.read() + "\n".encode("ascii"))
