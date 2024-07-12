import json
import hashlib
import os
from tqdm import tqdm

def hash_content(content):
    """Generate a SHA-256 hash for the given content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def remove_duplicates_and_count(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    print(f"Processing file: {input_file}")
    print(f"Number of items before cleaning: {len(data)}")

    seen_hashes = {}
    unique_items = []

    for item in tqdm(data, desc="Processing items"):
        content_hash = hash_content(item['content'])
        if content_hash in seen_hashes:
            seen_hashes[content_hash]['count'] += 1
        else:
            seen_hashes[content_hash] = {'item': item, 'count': 1}
            unique_items.append(item)

    # Update unique items with the count of duplicates
    for item in unique_items:
        content_hash = hash_content(item['content'])
        item['duplicate_count'] = seen_hashes[content_hash]['count']

    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(unique_items, file, ensure_ascii=False, indent=4)

    print(f"Number of items after cleaning: {len(unique_items)}")


if __name__ == "__main__":
    for filename in os.listdir('./json_eodhd/filtered'):
        input_file = os.path.join('./json_eodhd/filtered', filename)
        output_file = os.path.join('./json_eodhd/filtered', filename.replace('filtered', 'filtered-unique'))
        remove_duplicates_and_count(input_file, output_file)
