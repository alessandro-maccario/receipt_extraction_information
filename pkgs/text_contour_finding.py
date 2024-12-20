"""
This module preprocess the image by finding where the text is located and cutting the text
out of it by saving it into a single image.
"""

#######################
### IMPORT PACKAGES ###
#######################

import os
import sys
import cv2
import imutils
import numpy as np
from pathlib import Path

# Add the root folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pkgs.utils import folder_if_not_exist, merge_bounding_boxes


#######################
######## MAIN #########
#######################


class ContourFinding:
    def __init__(self, image_path) -> None:
        self.image_path = image_path
        self.ratio = 0

    def load_image(self):
        # Step 1: Load the image
        orig = cv2.imread(self.image_path)
        # need to copy the original because we will apply the transformation there
        copy = orig.copy()
        image = imutils.resize(copy, width=500)
        self.ratio = orig.shape[1] / float(image.shape[1])

        return image

    def inverse_binary(self):
        img = self.load_image()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # inverse binary image, to ensure text region is in white
        # because contours are found for objects in white
        inverse_binary_image = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )[1]
        # cv2.imwrite(
        #     "sandbox/receipts/test_inverse_binary.jpg", inverse_binary_image
        # )  # DRAW ALL

        return inverse_binary_image

    def fill_white_spots(self):
        # original image
        img = self.load_image()
        inverse_binary_image = self.inverse_binary()
        black = np.zeros([img.shape[0] + 2, img.shape[1] + 2], np.uint8)
        mask = cv2.floodFill(
            inverse_binary_image.copy(), black, (0, 0), 0, 0, 0, flags=8
        )[1]

        # cv2.imwrite("sandbox/receipts/test_masked_inverse_binary.jpg", mask)  # DRAW ALL
        return mask

    def dilation(self):
        mask = self.fill_white_spots()

        # dilation using horizontal kernel
        kernel_length = 500
        horizontal_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, (kernel_length, 1)
        )
        dilate = cv2.dilate(mask, horizontal_kernel, iterations=1)

        # cv2.imwrite(
        #     "sandbox/receipts/test_masked_dilated_inverse_binary.jpg", dilate
        # )  # DRAW ALL

        return dilate

    def deskew_angle(self, contours):
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        # Find largest contour and surround in min area box
        largestContour = contours[0]
        minAreaRect = cv2.minAreaRect(largestContour)

        # Determine the angle. Convert it to the value that was originally used to obtain skewed image
        angle = minAreaRect[-1]
        if angle < -45:
            angle = 90 + angle
        elif angle > 45:
            angle = angle - 90  # Handle cases where angle flips

        return angle

    # Rotate the image around its center
    def rotateImage(self, original, angle: float):
        # Step 1: Load the image
        newImage = original.copy()
        (h, w) = newImage.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        newImage = cv2.warpAffine(
            newImage, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        # cv2.imwrite("sandbox/receipts/output/deskew_rotate.jpg", newImage)

        return newImage

    def find_contours(self):
        # dilate the text to be more uniform
        dilate = self.dilation()
        # find the contours on the dilate image
        contours = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # contours = contours[0] if len(contours) == 2 else contours[1]
        return contours[0] if len(contours) == 2 else contours[1]

    def cut_bounding_box(self):
        # grab only the image name to be fed as a filename for the roi and the cut
        image_path = Path(self.image_path)
        image_name = image_path.name
        print("Processing Image:", image_name)

        # load the original image
        img = self.load_image()
        # keep a copy of the original image
        img2 = img.copy()
        # grab contours
        contours = self.find_contours()

        ############################
        # get the angle to rotate the image to be aligned with the left y-axis
        angle = self.deskew_angle(contours=contours)
        # deskew the image based on the angle
        img = self.rotateImage(original=img, angle=angle)
        ############################

        # Get bounding boxes from contours
        bounding_boxes = [cv2.boundingRect(c) for c in contours]
        # Merge overlapping or nearby bounding boxes
        merged_boxes = merge_bounding_boxes(bounding_boxes)

        for idx, (x, y, w, h) in enumerate(merged_boxes):
            # Cut and save the bounding box regions with the text, one image for each box
            # increment the height to include a bit more text in the bounded box
            h += 2
            roi = img[y : y + h, x : x + w]  # roi = region of interest
            # create folder if it does not exists, then save the file in it
            folder_if_not_exist(f"sandbox/receipts/output_roi/{image_name[:-4]}")
            cv2.imwrite(
                f"sandbox/receipts/output_roi/{image_name[:-4]}/{image_name[:-4]}_roi_{idx}.jpg",
                roi,
            )

            img_final = cv2.rectangle(img2, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # create folder if it does not exists, then save the file in it
        folder_if_not_exist(f"sandbox/receipts/output_cut/{image_name[:-4]}")
        # in the image_name[:-4] slice back until before the filetype

        # save the entire image with the bounding boxes around the text
        cv2.imwrite(
            f"sandbox/receipts/output_cut/{image_name[:-4]}/{image_name}", img_final
        )

        return img_final
