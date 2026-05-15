import os
import json
from tokenizer import tokenize, get_important_words, stem_tokens
from index_manager import add_to_index, offload_to_disk

def main():
    CORPUS_PATH = "/DEV" # Path to all 88 sub-domains
    OFFLOAD_THRESHOLD = 15000         # Offload to hit the "3 times" requirement 
    
    doc_count = 0
    partial_index_count = 0
    
    for domain_folder in os.listdir(CORPUS_PATH):
        folder_path = os.path.join(CORPUS_PATH, domain_folder)
        
        if not os.path.isdir(folder_path):
            continue
            
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                url = data["url"]           # The unique ID 
                html_content = data["content"] # The raw HTML string 
            
            # Get text from titles/headers first to mark as "important" 
            important_text = get_important_words(html_content)
            
            # Get all alphanumeric sequences from the page
            all_tokens = tokenize(html_content)
            stemmed_tokens = stem_tokens(all_tokens) # Porter Stemming
            
            # Build Inverted Index by passing tokens to the manager to update frequencies and doc IDs (right now only need freq)
            add_to_index(stemmed_tokens, url, important_text)
            
            doc_count += 1
            
            # offload to disk every so often
            if doc_count % OFFLOAD_THRESHOLD == 0:
                partial_index_count += 1
                offload_to_disk(f"partial_index_{partial_index_count}.json")
                # CRITICAL: Logic inside offload_to_disk must clear the memory map!

    merge_all_partial_indexes()
    
    print(f"Number of indexed documents: {doc_count}")
    print(f"Unique tokens: {get_unique_token_count()}")
    print(f"Index size on disk: {get_disk_usage_kb()} KB")

if __name__ == "__main__":
    main()