import cv2


class Deskewing:
    def __init__(self, image_path) -> None:
        self.cvImage = image_path

    # Calculate skew angle of an image
    def getSkewAngle(self) -> float:
        # Step 1: Load the image
        orig = cv2.imread(self.cvImage)
        # Prep image, copy, convert to gray scale, blur, and threshold
        newImage = orig.copy()
        gray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
        cv2.imwrite("sandbox/receipts/output/gray.jpg", gray)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        cv2.imwrite("sandbox/receipts/output/thres.jpg", thresh)

        # Apply dilate to merge text into meaningful lines/paragraphs.
        # Use larger kernel on X axis to merge characters into single line, cancelling out any spaces.
        # But use smaller kernel on Y axis to separate between different blocks of text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (250, 1))
        dilate = cv2.dilate(thresh, kernel, iterations=2)
        cv2.imwrite("sandbox/receipts/output/dilate.jpg", dilate)

        # Find all contours
        contours, hierarchy = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
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
    def rotateImage(self, angle: float):
        # Step 1: Load the image
        orig = cv2.imread(self.cvImage)
        newImage = orig.copy()
        (h, w) = newImage.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        newImage = cv2.warpAffine(
            newImage, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        cv2.imwrite("sandbox/receipts/output/deskew_rotate.jpg", newImage)

        # return newImage

    # Deskew image
    def deskew(self):
        angle = self.getSkewAngle()
        return self.rotateImage(-1.0 * angle)
