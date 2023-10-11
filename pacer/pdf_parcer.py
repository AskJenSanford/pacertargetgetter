import io
import fitz
from image_to_text import cropped_image, ocr_result

file_path = 'pdfs/177115599593.pdf'

pdf_file = fitz.open(file_path)

page_nums = len(pdf_file)

images_list = []

for page_num in range(page_nums):
    page_content = pdf_file[page_num]
    images_list.extend(page_content.get_images())

if len(images_list) == 0:
    raise ValueError(f'No images found in {file_path}')

for i, image in enumerate(images_list, start=1):
    xref = image[0]
    base_image = pdf_file.extract_image(xref)
    image_bytes = base_image['image']
    image = io.BytesIO(image_bytes)
    if i == 1:
        cropped_image(image, mid=False)
        address = ocr_result(mid=False)
    elif i == 2:
        cropped_image(image)
        address1 = ocr_result()
        cropped_image(image, mid=False)
        address2 = ocr_result(mid=False)

    # image_ext = base_image['ext']
    # image_name = str(i) + '.' + image_ext
    # with open(os.path.join("images", image_name), 'wb') as image_file:
    #     image_file.write(image_bytes)
    #     image_file.close()
