import fitz  # PyMuPDF
import os
from PIL import Image
from pdf2image import convert_from_path
import shutil
from docx import Document

from ImageInterpreter import ImageInterpreter

def ensure_folders_exist():
    required_folders = [
        'to_extract',
        'extracting',
        'output',
        'finished_extracting'
    ]
    
    for folder in required_folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created directory: {folder}")

def extract_images_and_text(pdf_path, output_folder, imgInt, width_threshold=500, height_threshold=500):
    # Skapa ett mappnamn baserat på PDF-filens namn
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    pdf_folder_path = os.path.join(output_folder, pdf_name)
    #pdf_folder_path = output_folder

    # Skapa mappen om den inte redan finns
    if not os.path.exists(pdf_folder_path):
        os.makedirs(pdf_folder_path)

    # Skapa ett filnamn för textfilen
    text_file_path = os.path.join(pdf_folder_path, pdf_name + '.txt')

    with open(text_file_path, 'w') as text_file:
        #check if pdf_path points to a pdf or a word file
        if pdf_path.endswith('.pdf'):
            extract_text_from_pdf(pdf_path, text_file_path, text_file, pdf_folder_path, imgInt, width_threshold, height_threshold)
        elif pdf_path.endswith('.docx'):
            extract_text_and_images_from_word(pdf_path, text_file_path, pdf_folder_path, imgInt, width_threshold, height_threshold)
        else:
            print(f"Unsupported file type: {pdf_path}")
            return
        

    return pdf_folder_path

def extract_text_and_images_from_word(word_file_path, text_file_path, output_folder, imgInt=None, width_threshold=500, height_threshold=500):
    # Öppna Word-dokumentet
    doc = Document(word_file_path)

    # Räknare för unika bildnamn
    image_counter = 1

    # Öppna textfilen för att skriva ut text och eventuella tolkningar
    with open(text_file_path, 'w', encoding='utf-8') as text_file:
        # Extrahera all text från dokumentet och bilder
        for paragraph_num, paragraph in enumerate(doc.paragraphs):
            text_file.write(paragraph.text + '\n')
            print(f"Extracting {text_file_path} from paragraph {paragraph_num + 1}")

            # Kontrollera om det finns en bild i detta stycke
            for run in paragraph.runs:
                if run.element.findall('.//w:drawing', namespaces=run.element.nsmap):
                    for shape in doc.inline_shapes:
                        if shape.type == 3:  # 3 betyder att det är en bild
                            image_path = os.path.join(output_folder, f'image_{image_counter}.png')
                            with open(image_path, 'wb') as f:
                                f.write(shape.image.blob)
                            print(f"Image saved as {image_path}")

                            # Bildtolkning, om imgInt är tillgänglig
                            if imgInt and should_interpret_image(image_path, width_threshold=width_threshold, height_threshold=height_threshold):
                                interpretation = imgInt.interpret_image(image_path)
                                print(f"Interpretation for {image_path}: {interpretation}")
                                text_file.write(f"[Bildtolkning image_{image_counter}.png: {interpretation}]\n")

                            image_counter += 1

        # Hantera eventuella bilder som inte är kopplade till stycken
        for shape in doc.inline_shapes:
            if shape.type == 3:  # 3 betyder att det är en bild
                image_path = os.path.join(output_folder, f'image_{image_counter}.png')
                if not os.path.exists(image_path):
                    with open(image_path, 'wb') as f:
                        f.write(shape.image.blob)
                    print(f"Additional image saved as {image_path}")

                    # Bildtolkning för ytterligare bilder
                    if imgInt and should_interpret_image(image_path, width_threshold=width_threshold, height_threshold=height_threshold):
                        interpretation = imgInt.interpret_image(image_path)
                        print(f"Interpretation for additional {image_path}: {interpretation}")
                        text_file.write(f"[Bildtolkning additional image_{image_counter}.png: {interpretation}]\n")

                    image_counter += 1     



def extract_text_from_pdf(pdf_path, text_file_path, text_file, pdf_folder_path, imgInt, width_threshold=500, height_threshold=500):
    # Öppna PDF-filen
        doc = fitz.open(pdf_path)

        # Loopa igenom varje sida i dokumentet
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            # Extrahera och skriv text till filen
            text = page.get_text()
            text_file.write(f'Sida {page_num + 1}\n{text}\n')
            print(f"Extracting {text_file_path} 'page {page_num + 1}")

            # Extrahera bilder
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]

                # Spara bildfilen
                img_filename = f'sida_{page_num + 1}_bild_{img_index + 1}.png'
                with open(os.path.join(pdf_folder_path, img_filename), 'wb') as img_file:
                    img_file.write(image_bytes)
                if should_interpret_image(os.path.join(pdf_folder_path, img_filename), width_threshold=width_threshold, height_threshold=height_threshold):
                    interpretation = imgInt.interpret_image(os.path.join(pdf_folder_path, img_filename))
                    print(f"interpretation {os.path.join(pdf_folder_path, img_filename)}: {interpretation}")
                    text_file.write(f"[Bildtolkning: {interpretation}]\n")

        doc.close()

def should_interpret_image(image_path, width_threshold=500, height_threshold=500):
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            if width >= width_threshold and height >= height_threshold:
                return True
            else:
                #print(f"Image {image_path} is too small to interpret.")
                return False
    except Exception as e:
        print(f"Error processing image {image_path}: {str(e)}")
        return False
    



def use_pdf2Image_method(pdf_path, output_folder):
    # Skapa ett mappnamn baserat på PDF-filens namn
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    pdf_folder_path = os.path.join(output_folder, pdf_name + "_pdf2image")

    # Skapa mappen om den inte redan finns
    if not os.path.exists(pdf_folder_path):
        os.makedirs(pdf_folder_path)

    # Konvertera varje sida i PDF-filen till en bild
    images = convert_from_path(pdf_path, dpi=600)  # dpi-värdet kan justeras beroende på önskad kvalitet

    # Spara varje bild
    for page_num, img in enumerate(images, start=1):
        img_filename = os.path.join(pdf_folder_path, f'sida_{page_num}.png')
        img.save(img_filename, 'PNG')

    print(f'Bilder sparade i {pdf_folder_path}')


#look in folder 'to_extract'
#for each file in that folder, move it to 'extracting', extract the text and save it to a file in the 'output' folder. Move the original file to 'finished_extracting



# Använd funktionen
def process_files():
    to_extract_folder = 'to_extract'
    extracting_folder = 'extracting'
    output_folder = 'output'
    finished_folder = 'finished_extracting'

    imgInt = ImageInterpreter(language="English")

    
    width_threshold = 150  # exempel på tröskelvärde för bredd
    height_threshold = 150  # exempel på tröskelvärde för höjd
    
    

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
            folder_path = extract_images_and_text(extracting_path, output_folder, imgInt, width_threshold, height_threshold)
            #text = extract_text_from_pdf_plumber(extracting_path)
            #if not text.strip():  # If no text extracted, assume it's a scanned PDF
            #    text = extract_text_from_scanned_pdf(extracting_path)
        except Exception as e:
            print(f"Error extracting text from {filename}: {str(e)}")
            text = ""        
        
        
        #low_qual = check_image_quality(folder_path, width_threshold, height_threshold)

        # Move original file to finished_extracting folder
        finished_path = os.path.join(finished_folder, filename)
        shutil.move(extracting_path, finished_path)

if __name__ == "__main__":
    ensure_folders_exist()
    process_files()

'''
pdf_path = 'to_extract/investor årsredovsning 2024.pdf'
output_folder = 'output'

imgInt = ImageInterpreter(language="English")

folder_path = extract_images_and_text(pdf_path, output_folder, imgInt)
width_threshold = 15  # exempel på tröskelvärde för bredd
height_threshold = 15  # exempel på tröskelvärde för höjd
low_qual = check_image_quality(folder_path, width_threshold, height_threshold)
if(low_qual> 0.2):
    use_pdf2Image_method(pdf_path, output_folder)
'''
