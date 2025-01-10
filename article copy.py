import os


class Article:
    def __init__(self):
        self.content = ""
        self.summary = ""
        self.file = ""
        self.file_path = ""

    def to_dict(self):
        return {
            "content": self.content,
            "summary": self.summary,
            "file": self.file,
            "file_path": self.file_path
        }

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
                
                # Set file (pdf or docx)
                for ext in ['.pdf', '.docx']:
                    original_file = os.path.join(folder, file.replace('summary_of_', '').replace('.txt', ext))
                    if os.path.exists(original_file):
                        article.file = original_file
                        break
                
                library.append(article)
        
        return library
    
    @staticmethod
    def get_summaries(library):
        summaries = []
        for article in library:
            article.summary = f"Följande sammanfattning är hämtad från artikel med file_path: {os.path.basename(article.file_path)}.\nSammanfattning:\n  {article.summary}\n\n "
            summaries.append(article.summary)
        return summaries
    
    @staticmethod
    def find_article_by_summary(summary, library):
        for article in library:
            if summary == article.summary:
                return article
        return None
    
    @staticmethod
    def get_article_content(filename, library):
        for article in library:
            if filename == os.path.basename(article.file_path):
                return article.content
        return None