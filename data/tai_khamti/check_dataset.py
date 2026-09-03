import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).parent

DATASET_FILE =(
    BASE_DIR
    / "TAI_KHAMTI_500.json"
)

print("="*70)
print("TAI KHAMTI DATASET QUALITY CHECK")
print("="*70)
with open(
    DATASET_FILE,
    "r",
    encoding="utf-8"
)as file:
    data= json.load(file)

print("\nTotal records:" , len(data))
required_fields =[
    "id",
    "category",
    "english",
    "tai_khamti",
    "transliteration"
]
missing_fields =[]
for item in data:
    for field in required_fields:
        if field not in item:
            missing_fields.append(
                (item.get("id"),field)
            )
print ("\n1. REQUIRED FIELD CHECK")
if missing_fields:
    print("❌ Missing fields found:")
    for record_id, field in missing_fields:
        print(
            f" ID{record_id}: missing {field}"
        )
else:
    print("✅ All required fields are present.")

empty_english =[]
empty_tai =[]
empty_transliteration =[]

for item in data:
    if not item["english"].strip():
        empty_english.append(item["id"])
    if not item["tai_khamti"].strip():
        empty_tai.append(item["id"])
    if not item["transliteration"].strip():
        empty_transliteration.append(item["id"])

print("\n2. EMPTY VALUE CHECK")
print(
    "Empty English:",
    len(empty_english)
)
print(
    "Empty Tai Khamti:",
    len(empty_tai)
)
print(
    "Empty Transliteration:",
    len(empty_transliteration)
)

english_questions = [
    item["english"].strip().lower()
    for item in data
]
duplicates = [
    english_questions
    for question, count
    in Counter(english_questions).items()
    if count>1
]
print("\n3. DUPLICATE QUESTION CHECK")
if duplicates:
    print(
        f"❌ {len(duplicates)} duplicate"
        "question found."
    )
    for question in duplicates:
        print(" ",question)
else:
    print("✅ No duplicate English questions.")

categories = Counter(
    item["category"]
    for item in data
)

print("\n4. CATEGORY DISTRIBUTION")
for category, count in categories.items():
    print(
        f"{category:<30}: {count}"
    )
short_english= []
short_tai =[]

long_english =[]
long_tai=[]
for item in data:
    english_length =len(
        item["english"]
    )
    tai_length =len(
        item["tai_khamti"]
    )
    if english_length<5:
        short_english.append(item["id"])
    if tai_length < 5:
        short_tai.append(item["id"])
    if english_length> 500:
        long_english.append(item["id"])
    if tai_length >500:
        long_tai.append(item["id"])

print("\n5.TEXT LENGTH CHECK")
print("Very short English:",len(short_english))
print("Very short Tai Khamti:",len(short_tai))
print("Very Long English:", len(long_english))
print("Very long Tai Khamti:",len(long_tai))
print("\n6. SAMPLE RECORDS")
print("-" *70)
for item in data[:5]:
    print("ID", item["id"])
    print("Category:",item["category"])
    print("English:",item["english"])
    print("Tai Khamti:",item["tai_khamti"])
    print("Transliteration:",item["transliteration"])
    print("_"*70)
print("\n" + "=" *70)

if(
    not missing_fields
    and not empty_english
    and not empty_tai
    and not duplicates
):
    print("✅ DATASET QUALITY CHECK PASSED")
else:
    print("⚠️ DATASET NEEDS ATTENTION")
print("="*70)
