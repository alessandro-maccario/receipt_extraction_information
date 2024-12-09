# Receipt Information Extraction

Tracking daily expenses is the first step in order to control one's financial situation.
A possible way of doing it is by:

- collect each and every receipt: usually not a problem
- manually enter the expenses in some kind of spreadsheet: very time consuming, especially if one wants to save each and every item bought with respective information (date, item, price).

In order to overcome this specific problem, the script `receipt_extraction_information.py` has been created. The script works as follow:

- collect the picture in a JPG format of the receipt. The higher the quality of the images, the better the final results. Data quality here is fundamental. The Script itself does already some preprocessing to extract the text, but an application such as `Genius Scan` for Android can be used to preprocess the image to be saved already as a scan of the receipt
- by using `cv2` it extracts bounding boxes where the text has been detected and save this images
- extract the text from each and every image by using `EasyOCR` and save the text in a txt file
- the text file is then parsed, cleaned and converted to a `pd.DataFrame` that is saved into a `csv` file
- the `csv` file is then read, converted to `md`, and ingested by `Llama 3.2 3B` to correct spelling mistakes and translate the content into English. Then saved back again into a csv file
- all the `csv` are then combined together in one single file to be then first checked and then inserted into a master table

Due to lack of high computing power, the LLM chosen is the best one that gives back a reasonable correct answer in a reasonable amount of time.

## Next Improvements

Possible improvements could focus on:

- save the data into a database
- use a more powerful model to extract the text directly from the receipt bypassing the need of image processing (a model such as ChatGPT could easily do that, but this lacks the privacy feature that I wanted to have)
- create a web app to share this project with other people more easily
- currently tested only with a restrict amount of receipts. Need for testing the Script with more receipts from different supermarkets and in different languages to address other extra information (noise) that should be removed from it.
