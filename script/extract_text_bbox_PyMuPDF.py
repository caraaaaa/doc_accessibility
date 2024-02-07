import fitz  # PyMuPDF
import os
from pathlib import Path

import argparse
import os

output_pdf_path = "text_bbox_2.pdf"
output_dir = "image_of_text"

parser = argparse.ArgumentParser(description="Extract text bounding boxes from a PDF and optionally create images or draw them.")
parser.add_argument('input_pdf_path', type=str, help="The path to the input PDF file.")
parser.add_argument('--output_pdf_path', type=str, help="The path for the output PDF file with bounding boxes.", default=output_pdf_path)
parser.add_argument("--text_img", action="store_true", help="Flag to save text blocks as images.")
parser.add_argument('--output_dir', type=str, help="The directory for the output text images.", default=output_dir)

def text_bbox_img(bbox, page, doc, output_dir, page_num, i):
    """
    Saves a text block as an image.
    """
    rect = fitz.Rect(bbox)
    pix = page.get_pixmap(clip=rect)
    filename = Path(doc.name).stem
    bbox_path = f"{output_dir}/image_{filename}_page_{page_num + 1}_block_{i + 1}.png"
    pix.save(bbox_path)

def extract_text_bbox_PyMyPDF(pdf_path, 
                                draw_bbox=False, output_pdf_path=None,
                                text_img=False, output_dir=None):
    """
    Extracts text bounding boxes from a PDF using PyMuPDF. Optionally draws them on the PDF or saves as images.
    """
    bounding_boxes = []

    # Open the PDF file
    doc = fitz.open(pdf_path)

    if text_img:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        print(f"Extract text image to directory {os.path.abspath(output_dir)}")

    # Iterate through each page in the document
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)

        # Get the list of text blocks
        blocks = page.get_text("dict")["blocks"]

        # Iterate over each block
        for i, block in enumerate(blocks):
            # Check if the block contains text (not an image)
            if block["type"] == 0:  # type 0 is text
                bbox = block["bbox"]  # Bounding box of the text block
                bounding_boxes.append((page_num, bbox))

                # Save the block as an image
                if text_img:
                    text_bbox_img(bbox, page, doc, output_dir, page_num, i)

                # Draw a rectangle around the text block
                if draw_bbox:
                    rect = fitz.Rect(bbox)
                    page.draw_rect(rect, color=(1, 0, 0), width=1.5)
        
    if draw_bbox:
        print(f"PDF with text bounding box output to {os.path.abspath(output_pdf_path)}")
        doc.save(output_pdf_path)

    # Close the document
    doc.close()

    return bounding_boxes # (x_0, y_0, x_1, x_1)

if __name__ == "__main__":
    args = parser.parse_args()

    extract_text_bbox_PyMyPDF(args.input_pdf_path, 
                              draw_bbox=True,
                              output_pdf_path=args.output_pdf_path,
                              text_img=args.text_img, 
                              output_dir=args.output_dir)