import os


content=""
summary=""
file=""
file_path=""

#this should be a class that has the above values as attributes
class Article:
    def __init__(self):
        self.content = ""
        self.summary = ""
        self.file = ""
        self.file_path = ""


#we should have a static method that can create a static library of articles from the files in the output folder. Content is the full .txt-file. Summary is the summary.txt of the content.txt-file. The file is the pdf or word that corresponds to the same name. The file_path is the path to the file.
    @staticmethod
    def create_library(folder):
        library = []
        for file in os.listdir(folder):
            if file.endswith('.txt') and file.startswith('summary_of_'):                
                article = Article()
                article.file_path = os.path.join(folder, file)
                
                # Set content
                content_path = os.path.join(folder, file.replace('summary_of_', ''))
                if os.path.exists(content_path):
                    with open(content_path, 'r') as f:
                        article.content = f.read()

                # Set summary
                with open(article.file_path, 'r') as f:
                    article.summary = f.read()
                
                # Set content
                content_path = os.path.join(folder, file.replace('summary_of_', ''))
                if os.path.exists(content_path):
                    with open(content_path, 'r') as f:
                        article.content = f.read()
                
                # Set file (pdf or docx)
                for ext in ['.pdf', '.docx']:
                    original_file = os.path.join(folder, file.replace('summary_of_', '').replace('.txt', ext))
                    if os.path.exists(original_file):
                        article.file = original_file
                        break
                
                library.append(article)
        
        return library
    
    #we should have a way of getting all summaries from the library
    @staticmethod
    def get_summaries(library):
        summaries = []
        for article in library:
            summaries.append(article.summary)
        return summaries
    
    #we should have a method that can take a summary and find the corresponding article in the library
    @staticmethod
    def find_article(summary, library):
        for article in library:
            if summary == article.summary:
                return article
        return None
    
    
