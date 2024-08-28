import fitz  
import pytesseract
from PIL import Image
import io
import re
import os
import sys

def extract_text_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    full_text = ""

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        text = page.get_text()
        full_text += text

    return full_text

def extract_images_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    images = []

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        image_list = page.get_images(full=True)

        for img in image_list:
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]

            image = Image.open(io.BytesIO(image_bytes))
            images.append(image)

    return images

def extract_text_from_images(images):
    all_matches = []

    for image in images:
        text = pytesseract.image_to_string(image)
        
        pattern = r'\b(10\d{5}|40\d{5})\b'
        matches = re.findall(pattern, text)
        all_matches.extend(matches)

    return all_matches

def find_numbers_in_pdf(pdf_path):
    full_text = extract_text_from_pdf(pdf_path)
    
    pattern = r'\b(10\d{5}|40\d{5})\b'
    text_matches = re.findall(pattern, full_text)
    
    images = extract_images_from_pdf(pdf_path)
    image_matches = extract_text_from_images(images)

    all_matches = text_matches + image_matches
    
    ten_matches = [number for number in all_matches if number.startswith("10")]
    forty_matches = [number for number in all_matches if number.startswith("40")]

    if len(ten_matches) > 1 and len(set(ten_matches)) > 1:
        return False, None
    if len(forty_matches) > 1 and len(set(forty_matches)) > 1:
        return False, None  
    if len(ten_matches) == 1 and len(forty_matches) == 1:
        return False, None  

    if len(ten_matches) == 1 or len(set(ten_matches)) == 1:
        return True, ten_matches[0]  
    if len(forty_matches) == 1 or len(set(forty_matches)) == 1:
        return True, forty_matches[0]  
    
    return False, None  

def main():
    if len(sys.argv) != 2:
        print("Usage: python.exe mytest.py <pdf_file>")
        sys.exit(1)

    pdf_file = sys.argv[1]

    if not os.path.exists(pdf_file):
        print(f"File {pdf_file} not found!")
        sys.exit(1)

    print(f"Processing {pdf_file}...")
    result, number = find_numbers_in_pdf(pdf_file)
    
    if result:
        new_file_name = f"{number}.pdf"
        os.rename(pdf_file, new_file_name)
        print(f"True - Valid matching number found: {number}. File renamed to {new_file_name}")
    else:
        print(f"False - Invalid matching number(s) found in {pdf_file}.")

if __name__ == "__main__":
    main()
