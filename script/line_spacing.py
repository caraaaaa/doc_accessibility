from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTAnno
import argparse

parser = argparse.ArgumentParser(description="Check line spacing in PDF.")
parser.add_argument('input_pdf_path', type=str, help="The path to the input PDF file.")

def calculate_line_spacing(font_size, y0_prev, y0_curr):
    """
    Calculates the line spacing and compares it to the font size.
    """
    if y0_prev is None:
        return False, float('inf')
    line_spacing = y0_prev - y0_curr
    return line_spacing<1.5*font_size, line_spacing/(1.5*font_size)

def check_line_spacing(input_pdf_path):
    """
    Checks the line spacing of text in a PDF file.
    """
    # Iterate through each page in the PDF
    for page_layout in extract_pages(input_pdf_path):
        y0_prev = None

        # Iterate through each layout element in the page
        for element in page_layout:
            # Check if the element is a text container (has text)
            if isinstance(element, LTTextContainer):
                # Iterate through each text line in the text container
                for text_line in element:
                    # Check if text_line actually a line of text
                    if not isinstance(text_line, LTChar) and not isinstance(text_line, LTAnno):
                        font_size = max(char.size for char in text_line if isinstance(char, LTChar))
                        y0_curr = text_line.y0

                        # Calculate line spacing and check for issues
                        spacing_issues, spacing_ratio = calculate_line_spacing(font_size, y0_prev, y0_curr)
                        if spacing_issues:
                            print(f"======= Line spacing issue at page {page_layout.pageid} ======")
                            print(f"Spacing ratio: {spacing_ratio}")
                            print(f"At line: {text_line.get_text()}")

                        y0_prev = y0_curr

if __name__ == "__main__":
    args = parser.parse_args()
    check_line_spacing(args.input_pdf_path)
