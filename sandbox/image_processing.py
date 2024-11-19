import cv2
import imutils
from imutils.perspective import four_point_transform


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
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
        # apply a four-point perspective transform to the *original* image to
        # obtain a top-down bird's-eye view of the receipt
        receipt = four_point_transform(orig, receiptCnt.reshape(4, 2) * self.ratio)

        ########################################
        #### TEST TO DRAW CONTOUR ####
        # print("COUNTOURS:", receiptCnt)
        orig = cv2.imread(self.image_path)
        original_copy = orig.copy()
        reshape_contours = (receiptCnt.reshape(4, 2) * self.ratio).astype(int)  # Reshape and scale

        con = cv2.drawContours(orig, [reshape_contours], -1, (0, 255, 0), 20)
        # save the contours in cropping variables
        [X, Y, W, H] = cv2.boundingRect(reshape_contours)
        # CUT THE PICTURE WITH BIGGEST BOX
        cropped_image = original_copy[Y : Y + H, X : X + W]
        cv2.imwrite("sandbox/test.jpg", con)  # DRAW ALL
        cv2.imwrite("sandbox/test_cut.jpg", cropped_image)

        # save transformed image
        cv2.imwrite("sandbox/receipt_topdown_view.jpg", imutils.resize(receipt, width=500))
