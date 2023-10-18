import io
import re
import fitz
import easyocr
from PIL import Image
from ..models import Address

reader = easyocr.Reader(['en'])
PATTERN = r'Jennifer Sanford, Plaintiff \d+\s+[A-Za-z\s,]+: \d+\s+[A-Za-z\s,]+\s+\d{5}'


class PDFImageProcessor:
    def __init__(self, file_number, case_number):
        self.file_path = f"case_pdf/{file_number}.pdf"
        self.pdf_file = fitz.open(self.file_path)
        self.images_list = []
        self.addresses = []
        self.case_number = case_number

    def extract_images(self):
        page_nums = len(self.pdf_file)

        for page_num in range(page_nums):
            page_content = self.pdf_file[page_num]
            self.images_list.extend(page_content.get_images())

        if len(self.images_list) == 0:
            raise ValueError(f'No images found in {self.file_path}')

    def process_images(self):
        for i, image in enumerate(self.images_list, start=1):
            xref = image[0]
            base_image = self.pdf_file.extract_image(xref)
            image_bytes = base_image['image']
            image = io.BytesIO(image_bytes)
            if i == 1:
                cropped_image(image, mid=False)
                address = ocr_result(mid=False)
                self.addresses.append(Address(case_number=self.case_number, address=address))
            elif i == 2:
                cropped_image(image)
                address = ocr_result()
                if address:
                    self.addresses.append(Address(case_number=self.case_number, address=address))

                cropped_image(image, mid=False)
                address = ocr_result(mid=False)
                if address:
                    self.addresses.append(Address(case_number=self.case_number, address=address))

        Address.objects.bulk_create(self.addresses)

        print(f"insert {self.case_number} addresses in database.")

    def start_pdf(self):
        self.extract_images()
        self.process_images()


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
