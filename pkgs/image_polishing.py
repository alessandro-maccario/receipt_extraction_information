"""Script to cut the image if there is too much border"""

import cv2
import imutils
import numpy as np
# from imutils.perspective import four_point_transform


class ImageProcessing:
    def __init__(self) -> None:
        self.image_path = "sandbox/receipts/original.jpg"
        self.ratio = 0

    def load_image(self):
        # Step 1: Load the image
        orig = cv2.imread(self.image_path)
        # need to copy the original because we will apply the transformation there
        copy = orig.copy()
        image = imutils.resize(copy, width=500)
        self.ratio = orig.shape[1] / float(image.shape[1])

        return image

    def edge_detection(self):
        # convert the image to grayscale, blur it slightly, and then apply
        # edge detection
        image = self.load_image()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(
            gray,
            (
                5,
                5,
            ),
            0,
        )
        edged = cv2.Canny(blurred, 75, 200)

        # save the image without the background and most of the content
        # cv2.imwrite("sandbox/receipt_edged.jpg", img_morphed)

        return edged

    def search_contour(self):
        # load the edged image
        edged = self.edge_detection()
        # find contours in the edge map and sort them by size in descending order
        cnts = cv2.findContours(
            edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        # initialize a contour that corresponds to the receipt outline
        receiptCnt = None

        #######################
        # load the original image
        orig = cv2.imread(self.image_path)

        #######################

        # loop over the contours
        for c in cnts:
            ################################
            con = cv2.drawContours(orig, [c], -1, (0, 255, 0), 20)

            ################################
            # approximate the contour
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            # if our approximated contour has four points, then we can
            # assume we have found the outline of the receipt
            if len(approx) == 4:
                receiptCnt = approx
                break

        cv2.imwrite("sandbox/receipts/test_search_contour.jpg", con)  # DRAW ALL

        # if the receipt contour is empty then our script could not find the
        # outline and we should be notified
        if receiptCnt is None:
            raise Exception(
                (
                    "Could not find receipt outline. "
                    "Try debugging your edge detection and contour steps."
                )
            )

        return receiptCnt

    def topdown_view(self):
        # load the original image
        orig = cv2.imread(self.image_path)
        receiptCnt = self.search_contour()

        # NOTE: this part has to be reviewed. The top down view should be integrated
        # NOTE: in the preprocess of the image
        ########################################
        #### TEST TO DRAW CONTOUR ####
        # print("COUNTOURS:", receiptCnt)

        # orig = cv2.imread(self.image_path)
        # original_copy = orig.copy()
        reshape_contours = (receiptCnt.reshape(4, 2) * self.ratio).astype(
            int
        )  # Reshape and scale

        # con = cv2.drawContours(receipt, [reshape_contours], -1, (0, 255, 0), 20)
        # save the contours in cropping variables
        [X, Y, W, H] = cv2.boundingRect(reshape_contours)
        # CUT THE PICTURE WITH BIGGEST BOX
        cropped_image = orig[Y : Y + H, X : X + W]
        # cv2.imwrite("sandbox/test.jpg", con)
        # save the receipt cropped image
        cv2.imwrite("sandbox/receipts/output/cut.jpg", cropped_image)

        # apply a four-point perspective transform to the *original* image to
        # obtain a top-down bird's-eye view of the receipt
        # receipt = self.four_point_transform(orig, receiptCnt.reshape(4, 2) * self.ratio)

        # # save transformed image
        # cv2.imwrite(
        #     "sandbox/receipts/output/orig_topdown_view.jpg",
        #     imutils.resize(receipt),
        # )

    # def order_points(self, pts):
    #     # initialzie a list of coordinates that will be ordered
    #     # such that the first entry in the list is the top-left,
    #     # the second entry is the top-right, the third is the
    #     # bottom-right, and the fourth is the bottom-left
    #     rect = np.zeros((4, 2), dtype="float32")

    #     # the top-left point will have the smallest sum, whereas
    #     # the bottom-right point will have the largest sum
    #     s = pts.sum(axis=1)
    #     rect[0] = pts[np.argmin(s)]
    #     rect[2] = pts[np.argmax(s)]

    #     # now, compute the difference between the points, the
    #     # top-right point will have the smallest difference,
    #     # whereas the bottom-left will have the largest difference
    #     diff = np.diff(pts, axis=1)
    #     rect[1] = pts[np.argmin(diff)]
    #     rect[3] = pts[np.argmax(diff)]

    #     # return the ordered coordinates
    #     return rect

    # def four_point_transform(self, image, pts):
    #     # obtain a consistent order of the points and unpack them
    #     # individually
    #     rect = self.order_points(pts)
    #     (tl, tr, br, bl) = rect

    #     # compute the width of the new image, which will be the
    #     # maximum distance between bottom-right and bottom-left
    #     # x-coordiates or the top-right and top-left x-coordinates
    #     widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    #     widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    #     maxWidth = max(int(widthA), int(widthB))

    #     # compute the height of the new image, which will be the
    #     # maximum distance between the top-right and bottom-right
    #     # y-coordinates or the top-left and bottom-left y-coordinates
    #     heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    #     heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    #     maxHeight = max(int(heightA), int(heightB))

    #     # now that we have the dimensions of the new image, construct
    #     # the set of destination points to obtain a "birds eye view",
    #     # (i.e. top-down view) of the image, again specifying points
    #     # in the top-left, top-right, bottom-right, and bottom-left
    #     # order
    #     dst = np.array(
    #         [
    #             [0, 0],
    #             [maxWidth - 1, 0],
    #             [maxWidth - 1, maxHeight - 1],
    #             [0, maxHeight - 1],
    #         ],
    #         dtype="float32",
    #     )

    #     # compute the perspective transform matrix and then apply it
    #     M = cv2.getPerspectiveTransform(rect, dst)
    #     warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    #     # return the warped image
    #     return warped
