import os
import json
from collections import defaultdict


def merge_partial_indexes(partial_files, output_file):

    merged_index = defaultdict(list)

    for file_name in partial_files:

        with open(file_name, "r") as f:
            partial_index = json.load(f)

        for token, postings in partial_index.items():

            merged_index[token].extend(postings)

    with open(output_file, "w") as f:
        json.dump(merged_index, f)

    for file_name in partial_files:
        os.remove(file_name)

    print(f"Merged index written to {output_file}")


def count_unique_tokens(index):
    return len(index)


def calculate_index_size(index_file):

    size_bytes = os.path.getsize(index_file)

    return round(size_bytes / 1024, 2)


def generate_report(index_file, document_count):

    with open(index_file, "r") as f:
        index = json.load(f)

    unique_tokens = count_unique_tokens(index)

    index_size = calculate_index_size(index_file)

    print("========== INDEX REPORT ==========")
    print(f"Documents Indexed: {document_count}")
    print(f"Unique Tokens: {unique_tokens}")
    print(f"Index Size on Disk: {index_size} KB")

# ==========================
# M2 SEARCH FUNCTIONS
# ==========================

def load_doc_id_map(file_path="doc_id_map.json"):

    with open(file_path, "r") as f:
        return json.load(f)


def convert_docids_to_urls(doc_ids, doc_map):

    urls = []

    for doc_id in doc_ids:

        doc_id = str(doc_id)

        if doc_id in doc_map:
            urls.append(doc_map[doc_id])

    return urls[:5]


def print_search_results(urls):

    print("\n===== TOP RESULTS =====\n")

    for i, url in enumerate(urls, start=1):
        print(f"{i}. {url}")