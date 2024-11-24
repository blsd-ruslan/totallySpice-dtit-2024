import os
from pdfrw import PdfReader
import pdfplumber
from pdf2image import convert_from_path
import pytesseract


# Function 1: Extract empty fields and their coordinates (AcroForm structure)
def extract_empty_fields_with_pdfrw(pdf_path):
    empty_fields = []
    pdf = PdfReader(pdf_path)
    if not pdf.Root.AcroForm or not pdf.Root.AcroForm.Fields:
        print("No AcroForm fields found.")
        return empty_fields

    fields = pdf.Root.AcroForm.Fields
    for field in fields:
        field_name = field.T if isinstance(field.T, str) else field.T.decode('utf-8', errors='ignore') if field.T else "Unnamed Field"
        field_value = field.V
        field_rect = field.Rect  # Coordinates [LLx, LLy, URx, URy]
        if not field_value:  # Check if the field is empty
            empty_fields.append({
                "name": field_name,
                "rect": list(map(float, field_rect))
            })
    return empty_fields


# Function 2: Extract text near empty fields using pdfplumber
def extract_text_near_fields(pdf_path, empty_fields, margin=20):
    nearby_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words()  # Extract words with coordinates
            for field in empty_fields:
                field_rect = field["rect"]
                for word in words:
                    x0, y0, x1, y1 = word['x0'], word['top'], word['x1'], word['bottom']
                    # Check if the word is within the margin of the field
                    if (
                            x0 >= field_rect[0] - margin and x1 <= field_rect[2] + margin and
                            y0 >= field_rect[1] - margin and y1 <= field_rect[3] + margin
                    ):
                        nearby_text.append({
                            "field": field["name"],
                            "page": page_num + 1,
                            "text": word['text']
                        })
    return nearby_text


# Function 3: Use OCR to extract nearby text for scanned PDFs
def extract_text_near_fields_with_ocr(pdf_path, empty_fields, margin=20, dpi=300):
    nearby_text = []
    pages = convert_from_path(pdf_path, dpi=dpi)
    for page_num, page_image in enumerate(pages):
        # Extract text with bounding boxes using OCR
        data = pytesseract.image_to_data(page_image, lang='eng', output_type=pytesseract.Output.DICT)
        for field in empty_fields:
            field_rect = field["rect"]
            for i, word in enumerate(data['text']):
                if word.strip():
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    # Check if word is near the field's coordinates
                    if (
                            x >= field_rect[0] - margin and (x + w) <= field_rect[2] + margin and
                            y >= field_rect[1] - margin and (y + h) <= field_rect[3] + margin
                    ):
                        nearby_text.append({
                            "field": field["name"],
                            "page": page_num + 1,
                            "text": word
                        })
    return nearby_text


# Main function to process the PDF
def process_pdf(pdf_path):
    # Extract empty fields
    print("Extracting empty fields...")
    empty_fields = extract_empty_fields_with_pdfrw(pdf_path)
    if not empty_fields:
        print("No empty fields found.")
        return

    print(f"Found {len(empty_fields)} empty fields:")
    for field in empty_fields:
        print(f" - {field['name']} at {field['rect']}")

    # Extract text near empty fields using pdfplumber
    print("\nExtracting text near empty fields (structured)...")
    text_near_fields = extract_text_near_fields(pdf_path, empty_fields)
    for item in text_near_fields:
        print(f"Field '{item['field']}' (Page {item['page']}): {item['text']}")

    # Extract text near empty fields using OCR
    print("\nExtracting text near empty fields (OCR for scanned PDFs)...")
    ocr_text_near_fields = extract_text_near_fields_with_ocr(pdf_path, empty_fields)
    for item in ocr_text_near_fields:
        print(f"Field '{item['field']}' (Page {item['page']}): {item['text']}")


# Run the script
if __name__ == "__main__":
    pdf_path = "docs/old.pdf"  # Replace with your PDF file path
    if os.path.exists(pdf_path):
        process_pdf(pdf_path)
    else:
        print(f"File '{pdf_path}' not found.")