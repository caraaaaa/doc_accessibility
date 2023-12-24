from fastai.learner import load_learner
from fastai.vision.widgets import PILImage
import pytesseract
from PIL import Image
import argparse
import os

parser = argparse.ArgumentParser(description="Check if the image is an image of text.")
parser.add_argument('input_pdf_path', type=str, help="The path to the input image file.")
parser.add_argument("--show_score", action="store_true", help="Show the classification score")

def is_image_of_text(img_path, show_score=False):
    """
    Determines if the provided image is primarily of text.
    """
    img = PILImage.create(img_path)
    learn = load_learner('model/imageOfText_classifier.pkl')
    pred,pred_idx,probs = learn.predict(img)

    if show_score:
        labels = learn.dls.vocab
        print({labels[i]: float(probs[i]) for i in range(len(labels))})

    return False if pred == 'False' else True

def perform_ORC(img_path):
    """
    Performs Optical Character Recognition (OCR) on the provided image.
    """
    img_obj=Image.open(img_path)
    text = pytesseract.image_to_string(img_obj)
    return text

if __name__ == "__main__":
    args = parser.parse_args()

    if is_image_of_text(args.input_pdf_path, show_score=args.show_score):
        print(f"File is an image of text: {os.path.abspath(args.input_pdf_path)}")
        text = perform_ORC(args.input_pdf_path)
        print("Text inside the image:")
        print(text)
    else:
        print(f"File is not an image of text: {os.path.abspath(args.input_pdf_path)}")
