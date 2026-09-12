from pathlib import Path

from backend.document_processing.text_splitter import document_splitter
from backend.rag.faiss_manager import faiss_manager


LANGUAGES = [
    "english",
    "hindi"
]


def build_vector_db(language):
    knowledge_file = Path("data") / language / "knowledge.txt"
    vector_db_path = Path("vector_db") / language

    if not knowledge_file.exists():
        print(f"❌ Knowledge file not found: {knowledge_file}")
        return

    print(f"\n📚 Building {language} knowledge base...")

    text = knowledge_file.read_text(encoding="utf-8")

    if not text.strip():
        print(f"❌ Knowledge file is empty: {knowledge_file}")
        return

    documents = document_splitter.split(
        text=text,
        source=f"{language}_knowledge.txt"
    )

    print(f"📝 Created {len(documents)} chunks")

    faiss_manager.create_and_save(
        documents=documents,
        vector_db_path=str(vector_db_path)
    )

    print(f"✅ {language} vector DB created at:")
    print(f"   {vector_db_path}")


def main():
    print("=" * 60)
    print("BUILDING LANGUAGE-SPECIFIC VECTOR DATABASES")
    print("=" * 60)

    for language in LANGUAGES:
        build_vector_db(language)

    print("\n" + "=" * 60)
    print("✅ DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()