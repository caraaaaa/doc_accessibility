"""
Convert Colors to Luminance:
The contrast ratio is based on the luminance (brightness) of the colors, 
not the colors themselves. Convert both the text and background colors to luminance. 
The formula for converting a color (RGB) to luminance is:

L = 0.2126*R+0.7152*G+0.0722*B

where R, G, and B are the red, green, and blue values of the color (normalized to 0-1).

Calculate Contrast Ratio:
The contrast ratio is calculated using the following formula:

Contrast Ratio = (L2+0.05) / (L1+0.05)

Where L1 is the luminance of the lighter color (either text or background) and 
L2 is the luminance of the darker color.
Ensure that L1 is always the luminance of the lighter of the two colors 
(either text or background).

Reference 
https://www.w3.org/WAI/WCAG21/Techniques/general/G18.html#procedure
https://juicystudio.com/services/luminositycontrastratio.php#specify
"""

from PIL import Image
import numpy as np
from scipy import stats
import argparse
import os

image_path = "sample_image/image2.png"
mask_path = "sample_image/image2_0.png"

parser = argparse.ArgumentParser(description="Calculate contrast ratio between text and background in an image.")
parser.add_argument('--image_path', type=str, help="The path for input images.", default=image_path)
parser.add_argument('--mask_path', type=str, help="The path for the segmentation mask", default=mask_path)

# Convert colors to luminance
def rgb_to_luminance(colors):
    colors = [c/255 if c > 1 else c for c in colors] # standardize
    colors = [c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4 for c in colors]
    return 0.2126 * colors[0] + 0.7152 * colors[1] + 0.0722 * colors[2]


def cal_contrast_ratio(image, mask, avg_color=False):
    # Extract text and background pixels
    text_pixels = image[np.where(mask > 0)]  # or whatever value represents text in your mask
    background_pixels = image[np.where(mask == 0)]

    # Calculate mode or average color for text and background
    if avg_color:
        text_color = np.mean(text_pixels, axis=0)
        background_color = np.mean(background_pixels, axis=0)
    else:
        text_color = stats.mode(text_pixels, axis=0).mode
        background_color = stats.mode(background_pixels, axis=0).mode
    # Convert colors to luminance
    luminance_text = rgb_to_luminance(text_color)
    luminance_background = rgb_to_luminance(background_color)

    # Ensure the higher luminance value is L1
    L1 = max(luminance_text, luminance_background)
    L2 = min(luminance_text, luminance_background)

    # Calculate contrast ratio
    contrast_ratio = (L1 + 0.05) / (L2 + 0.05)

    # Check against WCAG standard
    return contrast_ratio >= 4.5, contrast_ratio

if __name__ == "__main__":
    args = parser.parse_args()

    # Load the image and segmentation mask
    image = np.array(Image.open(args.image_path).convert('RGB'))
    mask = np.array(Image.open(args.mask_path).convert('L'))

    print(f"Text-background contrast of image {os.path.abspath(args.image_path)}")
    pass_standard, contrast_ratio = cal_contrast_ratio(image, mask)
    print("Pass" if pass_standard else "Fail", contrast_ratio)
