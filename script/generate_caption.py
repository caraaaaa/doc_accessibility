from transformers import AutoModelForCausalLM
from transformers import AutoProcessor
from PIL import Image
import torch
import os, warnings,logging
import argparse

# Suppress duplicate library warnings and general logging warnings
os.environ['KMP_DUPLICATE_LIB_OK']='True'
warnings.simplefilter('ignore')
logging.disable(logging.WARNING)

parser = argparse.ArgumentParser(description="Generate caption for non-text image.")
parser.add_argument('input_pdf_path', type=str, help="The path to the input PDF file.")

def generate_caption(img_path):
    """
    Generates a caption for a non-text image using a pre-trained model.
    """
    # load image
    image = Image.open(img_path).convert('RGB')

    # load model and processor
    processor = AutoProcessor.from_pretrained("microsoft/git-base")
    model = AutoModelForCausalLM.from_pretrained('model/finetuned_image_captioning', local_files_only=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    # prepare image for the model
    inputs = processor(images=image, return_tensors="pt").to(device)
    pixel_values = inputs.pixel_values

    # generate caption
    generated_ids = model.generate(pixel_values=pixel_values, max_length=50)
    generated_caption = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return generated_caption

if __name__ == "__main__":
    args = parser.parse_args()
    caption = generate_caption(args.input_pdf_path)
    print(caption)