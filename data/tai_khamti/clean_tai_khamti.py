import json
from pathlib import Path

from sqlalchemy.sql.crud import REQUIRED

BASE_DIR= Path(__file__).parent
INPUT_FILE = BASE_DIR /"raw"/"original_dataset.json"
OUTPUT_DIR = BASE_DIR / "cleaned"
OUTPUT_FILE= OUTPUT_DIR/ "tai_khamti_qa.json"

REQUIRED_FIELDS= [
    "category",
    "english",
    "tai_khamti_script",
    "transliteration"
]
print("="* 60)
print("TAI KHAMTI DATASET CLEANING")
print("="* 60)
print("\nLoading dataset...")
print("Input:",INPUT_FILE)
with open(INPUT_FILE,"r",encoding="utf-8")as file:
    data = json.load(file)

print("Original records:", len(data))


cleaned_data = []
seen = set()
removed_empty = 0
removed_duplicate = 0

for item in data:

    if not all(field in item for field in REQUIRED_FIELDS):
        removed_empty += 1
        continue
    category=str(item["category"]).strip()
    english =str(item["english"]).strip()
    tai_khamti= str(item["tai_khamti_script"]).strip()
    transliteration = str(item["transliteration"]).strip()

    if not english or not tai_khamti:
        removed_empty +=1
        continue
    duplicate_key =(
        english.lower(),
        tai_khamti,
        transliteration.lower()
    )
    if duplicate_key in seen:
        removed_duplicate +=1
        continue
    seen.add(duplicate_key)
    cleaned_data.append({
        "id": len(cleaned_data) + 1,
        "category": category,
        "english": english,
        "tai_khamti": tai_khamti,
        "transliteration": transliteration
    })
OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
)
with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
)as file:
    json.dump(
        cleaned_data,
        file,
        ensure_ascii=False,
        indent=2
    )
print("\nCleaning completed!")
print("-" * 60)
print("Original records :", len(data))
print("Cleaned records  :", len(cleaned_data))
print("Removed empty    :", removed_empty)
print("Removed duplicate:", removed_duplicate)
print("-" * 60)
print("\nOutput file:")
print(OUTPUT_FILE)
print("\n" + "=" * 60)
print("DONE")
print("=" * 60)