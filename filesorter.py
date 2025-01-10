import os
import shutil
import openai
from dotenv import load_dotenv

for root, dirs, files in os.walk('output'):
    for file in files:
        if file.endswith('.txt'):
            source_path = os.path.join(root, file)
            destination_path = os.path.join('output', file)
            shutil.move(source_path, destination_path)
            print(f"Moved {file} to output folder", end="")
#för varje .txt-fil i 'output' skicka den till openai 4o och sammanfatta den till en textfil i 'output' med namnet 'summary_of_{file}.txt'


# Set up OpenAI API key
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')


# Function to summarize text using OpenAI
def summarize_text(text, file_name):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=400,
        temperature=0.2,
        messages=[
            {"role": "system", "content": "Din uppgift är att beskriva en längre text. Den beskrivningen ska användas av en annan assistent för att avgöra vilken fil den kan behöva för att lösa en viss uppgift. Beskrivningen ska vara så kort som möjligt och göra det möjligt att avgöra om den filen är relevant för den fråga som den assistenten arbetar med."},
            {"role": "user", "content": f"Den text du får nu har namnet '{file_name}'. Beskriv denna text:\n\n{text}"}
        ]
    )
    return response.choices[0].message.content

# Process each .txt file in the 'output' directory
for file in os.listdir('output'):
    #if the file is txt and there is no summary file with the same name
    print("summarizing files")
    total_nr_of_files = sum(1 for file in os.listdir('output') if file.endswith('.txt') and not file.startswith('summary_of_'))    
    filecounter = 0
    if file.endswith('.txt') and not os.path.exists(os.path.join('output', f'summary_of_{file}')):
        file_path = os.path.join('output', file)
        
        # Read the content of the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Summarize the content
        summary = summarize_text(content, file_name=file)
        
        # Write the summary to a new file
        summary_file_name = f'summary_of_{file}'
        summary_file_path = os.path.join('output', summary_file_name)
        with open(summary_file_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        # Print progress
        filecounter += 1
        print(f"Processed {filecounter} out of {total_nr_of_files} files")
        #please make a progress bar that shows the progress of the summarizing
       

    print("Summarization complete")        

