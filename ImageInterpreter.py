import base64
import json
import os
import requests
import hashlib
from dotenv import load_dotenv

class ImageInterpreter:
    def __init__(self, cache_dir='cache', language='Swedish'):
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.language = language
        self.base_cache_dir = cache_dir
        if not os.path.exists(self.base_cache_dir):
            os.makedirs(self.base_cache_dir)

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def interpret_image(self, image_path):
        # Kontrollera cache först
        cache_key = self._generate_cache_key(image_path)
        cached_interpretation = self._get_cached_interpretation(cache_key)
        if cached_interpretation:
            return cached_interpretation

        # Om ingen cache finns, tolka bilden och spara tolkningen
        base64_image = self.encode_image(image_path)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        system_message = "Du är en AI-assistent med uppgift att tolka bilder för blinda individer. Beskriv bilden i detalj och fokusera på de element som skulle vara mest relevanta och intressanta för någon som inte kan se. Använd ett tydligt och beskrivande språk och undvik visuell jargong. Se till att din beskrivning är omfattande men ändå lätt att förstå. Se till att ditt svar är på det språk som den blinda personen förstår. Han förstår endast svenska."

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Tolka den här bilden. "
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1000
        }        
        '''payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f'Interpret this image as you would for a blind person. The person only speaks {self.language}. Make sure the person can understand the answer. '
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1000
        }'''

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        interpretation_json = response.json()
        print("---------")
        print("interpretation: ", interpretation_json)
        print("---------")

        # Extrahera svarssträngen från response
        interpretation = self._extract_interpretation(interpretation_json)
        
        # Spara i cache och returnera
        self._cache_interpretation(cache_key, interpretation)
        return interpretation

    def _extract_interpretation(self, interpretation_json):
        try:
            # Navigera genom JSON-objektet för att hitta rätt sträng
            return interpretation_json['choices'][0]['message']['content']
        except (KeyError, IndexError):
            # Om strukturen inte matchar som förväntat, returnera en felmeddelande
            return "Kunde inte tolka bilden."

    def _generate_cache_key(self, image_path):
        # Skapa en katalogstruktur baserad på image_path
        path_parts = image_path.split(os.path.sep)
        cache_dir = os.path.join(self.base_cache_dir, *path_parts[1:-1])
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        return os.path.join(cache_dir, os.path.basename(image_path))

    def _get_cached_interpretation(self, cache_key):
        cache_file = f'{cache_key}.txt'
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as file:
                return file.read()
        return None

    def _cache_interpretation(self, cache_key, interpretation):
        cache_file = f'{cache_key}.txt'
        with open(cache_file, 'w') as file:
            # Konvertera dictionary till JSON-sträng för lagring
            file.write(json.dumps(interpretation))
