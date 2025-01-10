#look in folder 'to_extract'
#for each file in that folder, move it to 'extracting', extract the text and save it to a file in the 'output' folder. Move the original file to 'finished_extracting
import os
import shutil

import pdfplumber

#skapa en metod som kan avgöra om en given fil är en pdf som innehåller text eller om den är inskannad text
def is_scanned_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            if page.extract_text().strip():
                return False  # If any page contains extractable text, it's not a scanned PDF
    return True  # If no extractable text is found, it's likely a scanned PDF



#skapa en metod som kan extrahera text från en inskannad pdf, dvs en som inte innehåller text


def extract_text_from_scanned_pdf(file_path):
    try:
        import pytesseract
        from PIL import Image
        import pdf2image
    except ImportError:
        print("Please install the required libraries: pytesseract, pillow, pdf2image")
        return ""

    text = ""
    # Convert PDF to list of images
    images = pdf2image.convert_from_path(file_path)

    for i, image in enumerate(images):
        # Perform OCR on each image
        page_text = pytesseract.image_to_string(image, lang='swe+eng')
        text += f"Page {i+1}:\n{page_text}\n\n"

    return text


def extract_text_from_pdf_plumber(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def process_files():
    to_extract_folder = 'to_extract'
    extracting_folder = 'extracting'
    output_folder = 'output'
    finished_folder = 'finished_extracting'

    # Create folders if they don't exist
    for folder in [extracting_folder, output_folder, finished_folder]:
        os.makedirs(folder, exist_ok=True)

    # Process each file in the to_extract folder
    for filename in os.listdir(to_extract_folder):
        file_path = os.path.join(to_extract_folder, filename)
        
        # Move file to extracting folder
        extracting_path = os.path.join(extracting_folder, filename)
        shutil.move(file_path, extracting_path)
        
        # Extract text
        #text = extract_text_from_pyPDF2(extracting_path)
        try:
            text = extract_text_from_pdf_plumber(extracting_path)
            if not text.strip():  # If no text extracted, assume it's a scanned PDF
                text = extract_text_from_scanned_pdf(extracting_path)
        except Exception as e:
            print(f"Error extracting text from {filename}: {str(e)}")
            text = ""        
        # Save extracted text to output folder
        output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.txt")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # Move original file to finished_extracting folder
        finished_path = os.path.join(finished_folder, filename)
        shutil.move(extracting_path, finished_path)

if __name__ == "__main__":
    process_files()
