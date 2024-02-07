import fitz
import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfFileReader, PdfFileWriter
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTAnno
import io
import os 
import argparse

output_pdf_path = 'readable_pdf.pdf'

parser = argparse.ArgumentParser(description="Convert a PDF to a searchable PDF.")
parser.add_argument('input_pdf_path', type=str, help="The path to the input PDF file.")
parser.add_argument('-o','--output_pdf_path', type=str, help="The path for the output searchable PDF file.", default=output_pdf_path)
parser.add_argument("-s", "--show_result", action="store_true", help="Show text of the searchable PDF after OCR")


def is_scanned_pdf(pdf_path):
    """
    Detects if the provided PDF is a scanned document by checking for the presence of text.
    """
    doc = fitz.open(pdf_path)
    text_found = False

    # Check if text found in any page
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text().strip()
        if text:
            text_found = True
            break
    doc.close()

    if not text_found:
        print("This PDF is likely a scanned document.")
    else:
        print("This PDF contains structured, readable text.")
    
    return not text_found


def create_searchable_pdf(input_pdf_path, output_pdf_path):
    """
    Converts scanned PDF images into text using Tesseract OCR and creates a new searchable PDF.
    """
    # Convert PDF to images
    images = convert_from_path(input_pdf_path)
    pdf_writer = PdfFileWriter()

    # Process each image/page
    for image in images:
        # Convert image to PDF using OCR
        page = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
        pdf = PdfFileReader(io.BytesIO(page))
        # Add OCR-processed page to PDF writer
        pdf_writer.addPage(pdf.getPage(0))

    # Save the new searchable PDF
    with open(output_pdf_path, "wb") as f:
        print(f"Searchable PDF is output to {os.path.abspath(output_pdf_path)}")
        pdf_writer.write(f)


def print_text(pdf_path):
    """
    Extract and print text content from a PDF file.
    """
    # Extract text from each page using pdfminer
    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            # Check if the element is a text container
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    # Ensure that the text line is not an annotation or character
                    if not isinstance(text_line, LTAnno) and not isinstance(text_line, LTChar):
                        print(text_line.get_text())


if __name__ == "__main__":
    args = parser.parse_args()

    if is_scanned_pdf(args.input_pdf_path):
        create_searchable_pdf(args.input_pdf_path, args.output_pdf_path)
        
        if args.show_result:
            print("=============== Before OCR =====================")
            print_text(args.input_pdf_path)

            print("=============== After OCR ======================")
            print_text(args.output_pdf_path)

