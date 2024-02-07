from cal_contrast import cal_contrast_ratio
from extract_text_bbox_PDFminer import extract_text_bbox_pdfminer
from extract_text_bbox_PyMuPDF import extract_text_bbox_PyMyPDF

from transformers import pipeline
import cv2
import numpy as np
from pathlib import Path
from pdf2image import convert_from_path
import fitz 

import argparse
import os

output_dir = "segmentation_model_output"
output_pdf_path = "bbox_low_contrast.pdf"

parser = argparse.ArgumentParser(description="Find low contrast text in a PDF document.")
parser.add_argument('input_pdf_path', type=str, help="The path to the input PDF file.")
parser.add_argument("--output_bbox_img", action="store_true", help="Option to save text block images with low contrast.")
parser.add_argument('--output_dir', type=str, help="The directory for output images.", default=output_dir)
parser.add_argument("--draw_bbox", action="store_true", help="Option to draw bounding boxes on low contrast text blocks.")
parser.add_argument('--output_pdf_path', type=str, help="The path for the output PDF file with drawn bounding boxes.", default=output_pdf_path)
parser.add_argument('--bbox_extractor', choices=['PyMyPDF', 'pdfminer'], help="Choice of bounding box extractor.", default='PyMyPDF')

def find_PDF_low_contrast(input_pdf_path, segmenter=None,
                          output_bbox_img=False, output_dir=None,
                          draw_bbox=False, output_pdf_path=None,
                          bbox_extractor="PyMyPDF"):
    """
    Identifies low contrast text in a PDF using segmentation and contrast ratio analysis.
    """

    # Initialize the segmenter model if not provided
    if not segmenter:
        segmenter = pipeline("image-segmentation", model="Caraaaaa/image_segmentation_text_v3")

    # Convert PDF to images
    images = convert_from_path(input_pdf_path)
    if draw_bbox: 
        doc = fitz.open(input_pdf_path)
        current_page = -1
    
    # Extract text bounding boxes
    if bbox_extractor == "PyMyPDF":
        bboxes = extract_text_bbox_PyMyPDF(input_pdf_path) # (x_0, y_0, x_1, x_1)
    else:
        bboxes = extract_text_bbox_pdfminer(input_pdf_path) # (x_0, y_0, x_1, x_1)

    # Calculate the scale factor
    original_dpi = 72  # Typical DPI of a PDF
    rendered_dpi = 200  # DPI used in pdf2image
    scale_factor = rendered_dpi / original_dpi

    # Create output directory if needed
    if output_bbox_img:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"\nExtract text image to directory {os.path.abspath(output_dir)}")
    
    # Process each bounding box
    for i, (page_id, bbox) in enumerate(bboxes):
        # Scale the bounding box to match the image size
        scaled_bbox = tuple(coordinate * scale_factor for coordinate in list(bbox))
        image = images[page_id]
        cropped_image = image.crop(scaled_bbox)

        # Get segmentation mask
        result = segmenter(cropped_image)

        if len(result) < 2:
            print(f"Cannot segment: {i} {bbox}")
            continue
        
        # Optionally save the model output mask
        if output_bbox_img:
            output_path = f'{output_dir}/{Path(input_pdf_path).stem}_bbox{i}.png'
            cv2.imwrite(output_path, np.array(cropped_image))
            output_path = f'{output_dir}/{Path(input_pdf_path).stem}_mask{i}.png'
            cv2.imwrite(output_path, np.array(result[1]['mask']))

        # Calculate contrast ratio
        image_np = np.array(cropped_image.convert('RGB'))
        mask_np = np.array(result[1]['mask'].convert('L')) 
        pass_standard, ratio = cal_contrast_ratio(image_np, mask_np)   
        print('bbox', i, "Pass" if pass_standard else "Fail", ratio)

        # Optionally draw bounding box for low contrast text
        if not pass_standard and draw_bbox:
            if page_id != current_page:
                page = doc.load_page(page_id)
                current_page = page_id
            rect = fitz.Rect(bbox)
            page.draw_rect(rect, color=(1, 0, 0), width=1.2) 
    
    # Save the modified PDF with bounding boxes
    if draw_bbox:
        print(f"\nOutput PDF with bounding box: {os.path.abspath(output_pdf_path)}")
        doc.save(output_pdf_path)
        doc.close()

if __name__ == "__main__":
    args = parser.parse_args()
    find_PDF_low_contrast(args.input_pdf_path,
                          output_bbox_img=args.output_bbox_img, 
                          output_dir=args.output_dir,
                          draw_bbox=args.draw_bbox, 
                          output_pdf_path=args.output_pdf_path,
                          bbox_extractor=args.bbox_extractor)

