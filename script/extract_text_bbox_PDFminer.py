from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBox, LTTextLine, LTChar, LTAnno
import fitz  # PyMuPDF
import argparse
import os

output_pdf_path = "text_bbox.pdf"

parser = argparse.ArgumentParser(description="Extract text bounding boxes from a PDF and optionally draw them.")
parser.add_argument('input_pdf_path', type=str, help="The path to the input PDF file.")
parser.add_argument('--output_pdf_path', type=str, help="The path for the output PDF file with bounding boxes.", default=output_pdf_path)

def extract_text_bbox_pdfminer(input_pdf_path, draw_bbox=False, output_path=None):
    """
    Extracts text bounding boxes from a PDF using PDFMiner and optionally draws them using PyMuPDF.
    """
    # Extract bounding boxes using PDFMiner
    bounding_boxes = []
    for page_layout in extract_pages(input_pdf_path):
        page_height = page_layout.height
        for element in page_layout:
            if isinstance(element, (LTTextBox, LTTextLine)) and element.get_text().strip():
                bbox = list(element.bbox)
                bbox[1], bbox[3] = bbox[3], bbox[1]
                bbox[1] = page_height - bbox[1] -1
                bbox[3] = page_height - bbox[3] -1
                bounding_boxes.append((page_layout.pageid-1, bbox))

    if draw_bbox:
        # Open the PDF with PyMuPDF
        doc = fitz.open(input_pdf_path)

        # Draw rectangles on the PDF
        current_page = -1
        for page_id, bbox in bounding_boxes:
            if page_id != current_page:
                page = doc.load_page(page_id)
                current_page = page_id
            rect = fitz.Rect(bbox)
            page.draw_rect(rect, color=(1, 0, 0), width=1.2)  # Red color

        # Save the modified PDF
        print(f"PDF with text bounding box output to {os.path.abspath(output_pdf_path)}")
        doc.save(output_path)
        doc.close()
    
    return bounding_boxes # (x_0, y_0, x_1, x_1)

if __name__ == "__main__":
    args = parser.parse_args()
    extract_text_bbox_pdfminer(args.input_pdf_path, draw_bbox=True, 
                               output_path=args.output_pdf_path)
