import cv2
import imutils
import numpy as np


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
        inverse_binary_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[
            1
        ]
        cv2.imwrite("sandbox/receipts/test_inverse_binary.jpg", inverse_binary_image)  # DRAW ALL

        return inverse_binary_image

    def fill_white_spots(self):
        # original image
        img = self.load_image()
        inverse_binary_image = self.inverse_binary()
        black = np.zeros([img.shape[0] + 2, img.shape[1] + 2], np.uint8)
        mask = cv2.floodFill(inverse_binary_image.copy(), black, (0, 0), 0, 0, 0, flags=8)[1]

        cv2.imwrite("sandbox/receipts/test_masked_inverse_binary.jpg", mask)  # DRAW ALL
        return mask

    def dilation(self):
        mask = self.fill_white_spots()

        # dilation using horizontal kernel
        kernel_length = 300
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))
        dilate = cv2.dilate(mask, horizontal_kernel, iterations=1)

        cv2.imwrite("sandbox/receipts/test_masked_dilated_inverse_binary.jpg", dilate)  # DRAW ALL

        return dilate

    def drawing_contours(self):
        img = self.load_image()
        dilate = self.dilation()

        img2 = img.copy()
        contours = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        for idx, c in enumerate(contours):
            x, y, w, h = cv2.boundingRect(c)
            # w += 10
            h += 2
            # cut and save the bounding box region with the text in a new image for each of them
            roi = img[y : y + h, x : x + w]  # roi = region of interest
            cv2.imwrite(f"sandbox/receipts/test_roi/roi_{idx}.jpg", roi)

            img_final = cv2.rectangle(img2, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imwrite("sandbox/receipts/test_contour_image.jpg", img_final)  # DRAW ALL

        return img_final
