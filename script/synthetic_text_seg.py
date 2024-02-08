import fitz
from PIL import Image, ImageDraw, ImageFont
import random
import string
import os
from pathlib import Path
import cv2
from pdf2image import convert_from_path
import numpy as np
import argparse

output_dir = 'image_of_text'
font_dir = 'font'

parser = argparse.ArgumentParser(description="Generate synthetic image of text with segmentation mask.")
parser.add_argument('--sample_no', type=int, help="Number of sample to generate", default=50)
parser.add_argument('--output_folder', type=str, help="The directory for the output images.", default=output_dir)
parser.add_argument('--font_folder', type=str, help="The directory for fonts", default=font_dir)


"""
Generate segmentation mask of text image from PDF
"""
def extract_text_blocks_as_images(pdf_path, output_folder):
    """
    Extracts text blocks from a PDF as individual images.
    """
    # Open the PDF file
    doc = fitz.open(pdf_path)

    # Create output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate through each page in the document
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)

        # Get the list of text blocks
        blocks = page.get_text("dict")["blocks"]

        # Iterate over each block
        for i, block in enumerate(blocks):
            # Check if the block contains text (not an image)
            if block["type"] == 0:
                rect = fitz.Rect(block["bbox"])
                pix = page.get_pixmap(clip=rect)

                # Save the block as an image
                filename = Path(doc.name).stem
                output_path = f"{output_folder}/image_{filename}_page_{page_num + 1}_block_{i + 1}.jpeg"
                pix.save(output_path)

    # Close the document
    doc.close()

def segment_text(image_path, output_dir, seg_mask=False):
    """
    Segments text from an image, generating a binary mask.
    """
    if Path(image_path).suffix == '.pdf':
         # Convert PDF to a list of images
        images = convert_from_path(image_path)
        image = [np.array(img) for img in images]
    else:
        # Read the image
        image = [cv2.imread(image_path)]

    for i, image in enumerate(image):
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)

        if seg_mask:
            thresh[thresh == 255] = 1

        # Save the mask
        output_path = f'{output_dir}/{Path(image_path).stem}_{i}.png'
        cv2.imwrite(output_path, thresh)

    return thresh



"""
Generate synthetic image of text with segmentation mask 
"""
def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def random_text():
    multiline = []
    for _ in range(random.randint(1, 5)):
        multiline.append(''.join(random.choice(string.ascii_letters + string.digits) for _ in range(random.randint(1, 10))))
    return '\n'.join(multiline)

def create_random_text_image(index, output_dir, font_list):
    """
    Creates a synthetic image of random text with a corresponding segmentation mask.
    """
    # Set random font size and path
    font_size = random.randint(30, 50)
    while True:
        try:
            font_path = random.choice(font_list)
            font = ImageFont.truetype(font_path, font_size)
            break
        except:
            pass
        print("OSError: unknown file format:", font_path)

    # Generate random text
    text = random_text()

    # Calculate text and image dimensions
    ascent, descent = font.getmetrics()
    line_heights = [font.getmask(line).getbbox()[3] + descent for line in text.split('\n')]
    height_text = sum(line_heights)+30
    text_length = max([font.getmask(line).getbbox()[2] for line in text.split('\n')])+20
    
    # Create image and draw the text
    image = Image.new('RGB', (text_length, height_text), color=random_color())
    draw = ImageDraw.Draw(image)
    draw.multiline_text((10, 0), text, font=font, fill=random_color())

    # Save the synthetic text image
    img_dir = f"{output_dir}/image"
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    output_path = f"{img_dir}/image{index}.jpeg"
    image.save(output_path)

    # Create and save the segmentation maske
    image = Image.new('RGB', (text_length, height_text), color=(1,1,1))
    draw = ImageDraw.Draw(image)
    draw.multiline_text((10, 0), text, font=font, fill=(2,2,2))
    image_gray = image.convert('L')

    anno_dir = f"{output_dir}/annotation"
    if not os.path.exists(anno_dir):
        os.makedirs(anno_dir)
    output_path = f"{anno_dir}/image{index}.png"
    image_gray.save(output_path)


if __name__ == "__main__":
    args = parser.parse_args()
    
    font_list = [os.path.join(font_dir, filename) for filename in os.listdir(args.font_folder) if Path(filename).suffix == '.ttf']
    
    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)

    print(f"Generating synthethic images of text to directory {os.path.abspath(args.output_folder)}")
    
    for index in range(args.sample_no):
        create_random_text_image(index, args.output_folder, font_list)