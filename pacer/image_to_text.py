import re
import easyocr
from PIL import Image

reader = easyocr.Reader(['en'])
PATTERN = r'Jennifer Sanford, Plaintiff \d+\s+[A-Za-z\s,]+: \d+\s+[A-Za-z\s,]+\s+\d{5}'


def cropped_image(imgage_path, mid=True):
    img = Image.open(imgage_path)
    h, w = img.size
    if mid:
        box = (1000, h - 1700, h, w - 2100)
    else:
        box = (20, h - 520, h, w)
    img2 = img.crop(box)

    img2.save('myimage_cropped.png')


def ocr_result(image_path="myimage_cropped.png", mid=True):
    results = reader.readtext(image_path)
    if mid:
        address = results[1][1]
    else:
        text = ''
        for result in results:
            text = f"{text} {result[1]}"

        match = re.search(PATTERN, text)
        if match:
            address = match.group()
        else:
            address = text.split("Sincerely")[-1].strip().lstrip(',')

    return address


# image_path = "images/1.png"
# cropped_image(image_path, mid=False)
# ocr_result("myimage_cropped.png", mid=False)
