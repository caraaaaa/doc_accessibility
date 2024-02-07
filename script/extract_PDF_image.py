import fitz
from PIL import Image
import io
import os
import argparse
from pathlib import Path
from image_of_text import is_image_of_text, perform_ORC
from generate_caption import generate_caption

output_folder='pdf_image'
output_pdf_path='image_bbox.pdf'

parser = argparse.ArgumentParser(description="Extract and process images from a PDF file.")
parser.add_argument('input_pdf_path', type=str, help="The path or directory to the input PDF file.")
parser.add_argument("--output_img", action="store_true", help="Output images extracted from the PDF.")
parser.add_argument('--output_folder', type=str, help="The directory for the output images.", default=output_folder)
parser.add_argument("--draw_bbox", action="store_true", help="Output PDF with bounding box on images.")
parser.add_argument('--output_pdf_path', type=str, help="The path for the output PDF file with bounding box.", default=output_pdf_path)
parser.add_argument('--captioning', action="store_true", help="Generate caption for images.")


def find_alt_text(doc, img):
    """
    Attempts to find alternative text (Alt Text) for an image in a PDF.
    """
    xref = img[0]
    img_metadata = doc.xref_get_key(xref, "Alt")

    if not img_metadata or img_metadata == ('null', 'null'):
        print(f"Image has no Alt Text.")
        return False
    else:
        print(f"Image has Alt Text: {img_metadata}")
        return True
        

def draw_bbox_pdf(page, img):
    """
    Draws a bounding box around an image on a PDF page.
    """
    bbox = page.get_image_bbox(img)
    print(f"Bounding box: {bbox}")
    page.draw_rect(bbox, color=(1, 0, 0), width=1.5)


def get_image_object(image, doc, output_folder='pdf_image', output_img=False):
    """
    Extracts an image from the PDF and optionally saves it to a file.
    """
    # Extract the image object using its xref
    xref = image[0]
    base_image = doc.extract_image(xref)
    image_bytes = base_image["image"]
    img_obj = Image.open(io.BytesIO(image_bytes))

    # Construct the output file path
    filename = Path(doc.name).stem
    output_file = f"{output_folder}/image_{filename}_{xref}.jpg"
    print(f"File path to the image {os.path.abspath(output_file)}")

    # Save the image to a file
    if output_img:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        rgb_im = img_obj.convert('RGB')
        rgb_im.save(open(output_file, "wb"))

    return img_obj, output_file
    

def find_non_text_content(input_pdf_path, 
                          output_img=True, output_folder='pdf_image',
                          draw_bbox=False, output_pdf_path='bbox_image.pdf',
                          captioning=False):
    """
    Processes images in a PDF to find non-text content, performing OCR or image captioning.
    """
    doc = fitz.open(input_pdf_path)

    # Iterate through each page
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)

       # Retrieve all images from the current page
        images = page.get_images(full=True)

        # Process each image
        for img_index, img in enumerate(images, start=1):
            print(f"\n========= Processing page {page_num + 1}, Image XREF: {img[0]} =========" )
            
            # Extract and optionally save the image
            img_obj, img_path = get_image_object(img, doc, 
                                                 output_folder=output_folder, 
                                                 output_img=output_img)
            
            # Check for alternative text for the image
            alt_text = find_alt_text(doc, img)

            if captioning:
                if os.path.exists(img_path):
                    # Classify the image as text or non-text
                    isText = is_image_of_text(img_path)

                    if isText:
                        # Perform OCR if it's an image of text
                        print(f"File is an image of text")
                        image_caption = perform_ORC(img_path)
                        print(f'ORC of the image: {image_caption}')
                    else:
                        # Perform image captioning if it's a non-text image
                        print(f"File is not an image of text")
                        image_caption = generate_caption(img_path)
                        print(f'Image Captioning: {image_caption}')
                else:
                    print("Filepath to the images doesn't exists")
                    print("Output images to perform classification and ORC/image captioning.")

            # Draw bounding box on the PDF for images without alt text
            if not alt_text and draw_bbox:
                draw_bbox_pdf(page, img)

            # TODO: Implement functionality to compare generated image caption with existing alt text
            
    # Save the modified PDF document if bounding boxes were drawn
    if draw_bbox:
        print(f"\nOutput PDF with bounding box: {os.path.abspath(output_pdf_path)}")
        doc.save(output_pdf_path)

    doc.close()

if __name__ == "__main__":
    args = parser.parse_args()

    if os.path.isdir(args.input_pdf_path):
        for filename in os.listdir(args.input_pdf_path):
            filepath = os.path.join(args.input_pdf_path, filename)
            if Path(filepath).suffix == '.pdf':
                    find_non_text_content(filepath, 
                            output_img=args.output_img, output_folder=args.output_folder,
                            draw_bbox=args.draw_bbox, output_pdf_path=args.output_pdf_path,
                            captioning=args.captioning)
    else:
        find_non_text_content(args.input_pdf_path, 
                            output_img=args.output_img, output_folder=args.output_folder,
                            draw_bbox=args.draw_bbox, output_pdf_path=args.output_pdf_path,
                            captioning=args.captioning)
