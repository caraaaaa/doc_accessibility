import fitz  # PyMuPDF
from langdetect import detect, DetectorFactory
import argparse

DetectorFactory.seed = 0  # Ensure consistent results from langdetect

parser = argparse.ArgumentParser(description="Detect the language of text in a PDF file.")
parser.add_argument('input_pdf_path', type=str, help="The path to the input PDF file.")
    
def check_language_property(pdf_path):
    """
    Checks the language property in the metadata of a PDF document.
    """
    # Open the PDF
    doc = fitz.open(pdf_path)

    # Access document metadata
    metadata = doc.metadata
    language = metadata.get('lang', 'Language not specified')

    # Close the document
    doc.close()

    return language

def detect_language(text):
    """
    Detects the language of a given text.
    """
    try:
        return detect(text)
    except:
        return "Language detection failed"

def extract_and_detect_language(pdf_path):
    """
    Extracts text from each page of a PDF and detects its language.
    """
    # Open the PDF file
    doc = fitz.open(pdf_path)
    languages = []

    # Iterate through each page
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()

        if text.strip():  # Check if there is text on the page
            language = detect_language(text)
            languages.append(language)

    doc.close()

    # Handling multi-language case
    if len(set(languages)) > 1:
        return f"Multi-language document, detected languages: {set(languages)}"
    elif languages:
        return f"Single language document, detected language: {languages[0]}"
    else:
        return "No detectable text found in the document"

if __name__ == "__main__":
    args = parser.parse_args()

    language = check_language_property(args.input_pdf_path)
    print(f"Lauguage property: {language}")

    result = extract_and_detect_language(args.input_pdf_path)
    print(result)
