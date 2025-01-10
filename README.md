# PDF Extraktor

A Python tool for extracting text and images from PDF and Word documents, with optional image interpretation capabilities.

## Features

- Extract text and images from PDF files
- Extract text and images from Word (.docx) files
- Optional image interpretation for images above specified dimensions
- Batch processing of documents
- Organized output structure

## Requirements

- Python 3.x
- PyMuPDF (fitz)
- Pillow
- pdf2image
- python-docx

## Installation

1. Clone the repository: 
```bash
git clone https://github.com/Ztein/pdfextraktor.git
cd pdfextraktor
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Create the following directories in the project root:
   - `to_extract`: Place your PDF/Word files here
   - `extracting`: Temporary processing directory (created automatically)
   - `output`: Where extracted content will be saved
   - `finished_extracting`: Where processed files are moved

2. Run the script:
```bash
python extraktor.py
```

## Output Structure

For each processed file, the script creates:
- A folder named after the input file
- A text file containing extracted text
- Image files extracted from the document
- Image interpretations (if enabled and images meet size thresholds)

## License

[MIT License](LICENSE)
3. The script will process all files in the `to_extract` directory, extract text and images, and save the results in the `output` directory.

4. The script will also move processed files to the `finished_extracting` directory.

