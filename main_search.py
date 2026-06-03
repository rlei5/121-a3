import json
import time
from search_engine import SearchEngine
from analytics_merger import load_doc_id_map, convert_docids_to_urls, print_search_results

INDEX_FILE = "final_index.json"
DOC_ID_MAP_FILE = "doc_id_map.json"
SEEK_TABLE_FILE = "seek_table.json"
METADATA_FILE = "metadata.json"

def main():
    print("Loading index...")
    with open(SEEK_TABLE_FILE, "r", encoding="utf-8") as f:
        seek_table = json.load(f)
    doc_map = load_doc_id_map(DOC_ID_MAP_FILE)
    engine = SearchEngine(INDEX_FILE, SEEK_TABLE_FILE, METADATA_FILE)

    print("========== SEARCH ENGINE ==========")
    while True:
        query = input("\nSearch (or 'quit' to exit): ").strip()
        if query.lower() == "quit":
            break
        if not query:
            continue

        start = time.time()
        doc_ids = engine.scored_query(query)
        urls = convert_docids_to_urls(doc_ids, doc_map)
        elapsed = round((time.time() - start) * 1000, 2)

        print_search_results(urls)
        print(f"({elapsed} ms)")

if __name__ == "__main__":
    main()