import os
import json
from tokenizer import tokenize, get_important_tokens, stem_tokens
from index_manager import update_inverted_index, offload_to_disk
from analytics_merger import merge_partial_indexes, generate_report

CORPUS_PATH = os.path.join(os.path.dirname(__file__), "DEV")
OFFLOAD_THRESHOLD = 15000
FINAL_INDEX = "final_index.json"

def main():
    doc_count = 0
    partial_index_count = 0
    partial_files = []
    doc_id_map = {}  # doc_id -> url

    for domain_folder in os.listdir(CORPUS_PATH):
        folder_path = os.path.join(CORPUS_PATH, domain_folder)

        if not os.path.isdir(folder_path):
            continue

        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                url = data["url"]
                html_content = data["content"]
            except (json.JSONDecodeError, KeyError):
                continue

            doc_count += 1
            doc_id_map[doc_count] = url

            if doc_count % 1000 == 0:
                print(f"Indexed {doc_count} documents...")

            all_tokens = stem_tokens(tokenize(html_content))
            important_tokens = stem_tokens(get_important_tokens(html_content))

            update_inverted_index(doc_count, all_tokens, important_tokens)

            if doc_count % OFFLOAD_THRESHOLD == 0:
                partial_index_count += 1
                partial_file = f"partial_index_{partial_index_count}.json"
                offload_to_disk(partial_file)
                partial_files.append(partial_file)

    # offload any remaining in-memory index
    if doc_count % OFFLOAD_THRESHOLD != 0:
        partial_index_count += 1
        partial_file = f"partial_index_{partial_index_count}.json"
        offload_to_disk(partial_file)
        partial_files.append(partial_file)

    merge_partial_indexes(partial_files, FINAL_INDEX)

    with open("doc_id_map.json", "w") as f:
        json.dump(doc_id_map, f)

    generate_report(FINAL_INDEX, doc_count)

if __name__ == "__main__":
    main()