import json
from pathlib import Path

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

BASE_DIR = Path(__file__).parent
OLD_DATASET_FILE = BASE_DIR  / "datasets" / "TAI_KHAMTI_500.json"
NEW_DATASET_FILE = BASE_DIR /"datasets" / "tribal_knowledge_phase2_4.json"
FAISS_DIR = BASE_DIR / "faiss_index"
INDEX_FILE = FAISS_DIR / "tai_khamti_combined.index"
DATA_FILE = FAISS_DIR / "tai_khamti_combined_documents.json"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def load_datasets():
    print("=" * 70)
    print("TAI KHAMTI COMBINED FAISS KNOWLEDGE BASE")
    print("=" * 70)
    print("\nLoading OLD dataset...")
    print("Dataset:", OLD_DATASET_FILE)

    if not OLD_DATASET_FILE.exists():
        raise FileNotFoundError(
            f"\nOld dataset not found:\n{OLD_DATASET_FILE}"
        )
    with open(
        OLD_DATASET_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        old_data = json.load(file)
    print(f"Loaded {len(old_data)} records from TAI_KHAMTI_500.")

    print("\nLoading NEW Phase dataset...")
    print("Dataset:", NEW_DATASET_FILE)
    if not NEW_DATASET_FILE.exists():
        raise FileNotFoundError(
            f"\nNew Phase 2.4 dataset not found:\n"
            f"{NEW_DATASET_FILE}"
        )
    with open(NEW_DATASET_FILE, "r",encoding="utf-8"
    ) as file:
        new_data = json.load(file)
    print(f"Loaded {len(new_data)} records from NEW dataset.")
    return old_data, new_data

def create_documents(old_data, new_data):
    documents = []
    print("\nProcessing OLD dataset...")
    for item in old_data:
        document = {
            "id": item["id"],
            "category": item["category"],
            "english": item["english"],
            "tai_khamti": item["tai_khamti"],
            "transliteration": item["transliteration"],
            "source": "TAI_KHAMTI_500"
        }
        documents.append(document)
    print("Processing NEW Phase dataset...")
    for index, item in enumerate(new_data):
        document = {
            "id": f"phase2_4_{index + 1}",
            "category": item["category"],
            "english": item["answer"],
            "tai_khamti": item["answer_tai_khamti"],
            "transliteration": "",
            "instruction": item["instruction"],
            "source": "PHASE_2_4"
        }

        documents.append(document)
    print("\n" + "=" * 70)
    print("DATASET COMBINATION COMPLETE")
    print("=" * 70)
    print("Old dataset records :", len(old_data))
    print("NEW Dataset records:", len(new_data))
    print("TOTAL documents        :", len(documents))
    return documents

def create_embedding_text(document):
    instruction = document.get("instruction", "")
    return (
        f"Category: {document['category']}\n"
        f"Question: {instruction}\n"
        f"English: {document['english']}\n"
        f"Tai Khamti: {document['tai_khamti']}\n"
        f"Transliteration: {document['transliteration']}\n"
        f"Source: {document['source']}"
    )
def build_faiss_index(documents, model):
    print("\n" + "=" * 70)
    print("CREATING EMBEDDINGS")
    print("=" * 70)

    texts = [
        create_embedding_text(document)
        for document in documents
    ]
    print(
        f"\nCreating embeddings for "
        f"{len(texts)} documents..."
    )
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )
    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )
    print("\nEmbeddings shape:", embeddings.shape)

    faiss.normalize_L2(embeddings)
    dimension = embeddings.shape[1]
    print("Embedding dimension:", dimension)
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    print("\nFAISS index created.")
    print("Documents stored:", index.ntotal)
    return index
def save_knowledge_base(index, documents):
    FAISS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )
    faiss.write_index(
        index,
        str(INDEX_FILE)
    )
    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            documents,
            file,
            ensure_ascii=False,
            indent=2
        )
    print("\n" + "=" * 70)
    print("FAISS KNOWLEDGE BASE SAVED")
    print("=" * 70)
    print("FAISS index :", INDEX_FILE)
    print("Documents   :", DATA_FILE)

def test_search(index, documents, model):
    print("\n" + "=" * 70)
    print("TESTING FAISS SEARCH")
    print("=" * 70)
    test_questions = [
        "What is artificial intelligence?",
        "What is machine learning?",
        "What is soil conservation?"
    ]

    for test_question in test_questions:
        print("\n" + "-" * 70)
        print("Test question:", test_question)
        query_embedding = model.encode(
            [test_question],
            convert_to_numpy=True
        ).astype("float32")
        faiss.normalize_L2(query_embedding)
        scores, indices = index.search(
            query_embedding,
            3
        )
        print("\nTOP 3 RESULTS:\n")
        for rank, (score, idx) in enumerate(
            zip(scores[0], indices[0]),
            start=1
        ):
            document = documents[idx]
            print(f"Result {rank}")
            print(f"Score: {score:.4f}")
            print(f"Source: {document['source']}")
            print(f"Category: {document['category']}")
            print(f"English: {document['english']}")
            print(
                f"Tai Khamti: "
                f"{document['tai_khamti']}"
            )
            if document.get("instruction"):
                print(
                    f"Question: "
                    f"{document['instruction']}"
                )
            print("-" * 70)
def main():
    old_data, new_data = load_datasets()
    documents = create_documents(
        old_data,
        new_data
    )
    print("\n" + "=" * 70)
    print("LOADING EMBEDDING MODEL")
    print("=" * 70)
    print(f"Model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(
        EMBEDDING_MODEL
    )
    print("Embedding model loaded.")
    texts = [
        create_embedding_text(document)
        for document in documents
    ]
    print(
        f"\nCreating embeddings for "
        f"{len(texts)} documents..."
    )
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )
    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )
    faiss.normalize_L2(embeddings)
    dimension = embeddings.shape[1]
    print("\nEmbedding dimension:", dimension)
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    print(
        "\nFAISS index created."
    )
    print(
        "Number of vectors:",
        index.ntotal
    )
    save_knowledge_base(
        index,
        documents
    )
    test_search(
        index,
        documents,
        model
    )
    print("\n" + "=" * 70)
    print("SUCCESSFULLY COMPLETED")
    print("=" * 70)
if __name__ == "__main__":
    main()