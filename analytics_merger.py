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