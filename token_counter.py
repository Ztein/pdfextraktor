#use tiktoken on each file in 'output' and calculate how many tokens are in each file
import os
import tiktoken

def count_tokens(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    enc = tiktoken.encoding_for_model("gpt-4o")
    tokens = enc.encode(content)
    return len(tokens)

output_dir = 'output'
token_counts = {}
total_tokens = 0
for filename in os.listdir(output_dir):
    if filename.endswith('.txt') and filename.startswith('summary_of_'):        
        file_path = os.path.join(output_dir, filename)
        token_count = count_tokens(file_path)
        token_counts[filename] = token_count

for filename, count in token_counts.items():
    total_tokens += count
    print(f"{filename}: {count} tokens")

print(f"Total tokens: {total_tokens}")