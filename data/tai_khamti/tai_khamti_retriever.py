
"""
Tai Khamti Retriever
Responsibilities:
- Lazy-load FAISS
- Lazy-load embedding model
- Exact English -> Tai Khamti matching
- Exact Tai Khamti -> English matching
- Semantic retrieval
- Lightweight lexical/category relevance
- Return multiple relevant documents for RAG
"""
import json
import re
from pathlib import Path
class TaiKhamtiRetriever:
    def __init__(self, top_k=5, similarity_threshold=0.50):
        print("=" * 70)
        print("INITIALIZING TAI KHAMTI RETRIEVER")
        print("=" * 70)
        base_dir = Path(__file__).parent
        self.index_file = base_dir / "faiss_index" / "tai_khamti_combined.index"
        self.documents_file = base_dir / "faiss_index" / "tai_khamti_combined_documents.json"
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.index = None
        self.documents = None
        self.model = None
        print("Tai Khamti Retriever created.")
        print("FAISS index: NOT loaded yet.")
        print("Documents: NOT loaded yet.")
        print("Embedding model: NOT loaded yet.")
    @staticmethod
    def normalize_text(text):
        if not text:
            return ""
        text = str(text).lower().strip()
        text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
    @staticmethod
    def tokenize(text):
        normalized = TaiKhamtiRetriever.normalize_text(text)
        return set(normalized.split()) if normalized else set()
    def load_database(self):
        if self.index is not None and self.documents is not None:
            return
        print("=" * 70)
        print("LOADING TAI KHAMTI DATABASE")
        print("=" * 70)
        import faiss
        if not self.index_file.exists():
            raise FileNotFoundError(f"Tai Khamti FAISS index not found: {self.index_file}")
        if not self.documents_file.exists():
            raise FileNotFoundError(f"Tai Khamti documents not found: {self.documents_file}")
        print("Loading FAISS index...")
        self.index = faiss.read_index(str(self.index_file))
        print("FAISS index loaded.")
        print("Loading Tai Khamti documents...")
        with open(self.documents_file, "r", encoding="utf-8") as file:
            self.documents = json.load(file)
        if not isinstance(self.documents, list):
            raise ValueError("Tai Khamti documents JSON must contain a list.")
        print(f"Loaded {len(self.documents)} documents.")
        print(f"FAISS documents: {self.index.ntotal}")
        if self.index.ntotal != len(self.documents):
            raise ValueError("FAISS index size and document count do not match. Rebuild the index before searching.")
        print("Tai Khamti database loaded successfully.")
    def load_model(self):
        if self.model is not None:
            return
        print("=" * 70)
        print("LOADING TAI KHAMTI EMBEDDING MODEL")
        print("=" * 70)
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        print("Tai Khamti embedding model loaded.")
    def exact_match_search(self, question):
        self.load_database()
        normalized_question = self.normalize_text(question)
        if not normalized_question:
            return None
        searchable_fields = ("instruction", "english", "tai_khamti", "transliteration")
        for document in self.documents:
            for field in searchable_fields:
                field_value = self.normalize_text(document.get(field, ""))
                if field_value and field_value == normalized_question:
                    result = dict(document)
                    result["score"] = 1.0
                    result["semantic_score"] = 1.0
                    result["lexical_score"] = 1.0
                    result["source"] = "TAI_KHAMTI_EXACT"
                    result["matched_field"] = field
                    print(f"EXACT MATCH FOUND IN FIELD: {field}")
                    print(f"ID: {document.get('id', 'N/A')}")
                    return result
        return None
    def lexical_score(self, question, document):
        query_tokens = self.tokenize(question)
        if not query_tokens:
            return 0.0
        searchable_text = " ".join([
            document.get("instruction", ""),
            document.get("english", ""),
            document.get("tai_khamti", ""),
            document.get("transliteration", ""),
            document.get("category", "")
        ])
        document_tokens = self.tokenize(searchable_text)
        if not document_tokens:
            return 0.0
        overlap = query_tokens.intersection(document_tokens)
        return len(overlap) / max(len(query_tokens), 1)
    def semantic_search(self, question, top_k=None):
        self.load_database()
        self.load_model()
        import numpy as np
        if top_k is None:
            top_k = self.top_k
        if not self.documents or self.index.ntotal == 0:
            return []
        candidate_k = min(max(top_k * 3, 10), self.index.ntotal)
        embedding = self.model.encode([question], convert_to_numpy=True, normalize_embeddings=True)
        embedding = np.asarray(embedding, dtype="float32")
        scores, indices = self.index.search(embedding, candidate_k)
        candidates = []
        for score, index_position in zip(scores[0], indices[0]):
            if index_position < 0 or index_position >= len(self.documents):
                continue
            document = self.documents[index_position]
            semantic_score = float(score)
            lexical_score = self.lexical_score(question, document)
            combined_score = semantic_score * 0.80 + lexical_score * 0.20
            result = dict(document)
            result["semantic_score"] = semantic_score
            result["lexical_score"] = lexical_score
            result["score"] = combined_score
            result["source"] = "TAI_KHAMTI_SEMANTIC"
            candidates.append(result)
        candidates.sort(key=lambda item: item.get("score", 0.0), reverse=True)
        final_results = []
        seen_ids = set()
        for result in candidates:
            result_id = result.get("id")
            if result_id in seen_ids:
                continue
            seen_ids.add(result_id)
            if result["semantic_score"] < self.similarity_threshold:
                continue
            final_results.append(result)
            if len(final_results) >= top_k:
                break
        return final_results
    def search(self, question, top_k=None):
        if not question or not str(question).strip():
            return []
        if top_k is None:
            top_k = self.top_k
        print("\n" + "=" * 70)
        print("TAI KHAMTI SEARCH")
        print("=" * 70)
        print(f"Question: {question}")
        exact_result = self.exact_match_search(question)
        if exact_result:
            print("Returning exact verified match.")
            return [exact_result]
        print("No exact match.")
        print("Performing multi-document semantic search...")
        results = self.semantic_search(question=question, top_k=top_k)
        print(f"Retrieved {len(results)} Tai Khamti documents.")
        for rank, result in enumerate(results, start=1):
            print(f"{rank}. ID={result.get('id', 'N/A')} score={result.get('score', 0):.4f} semantic={result.get('semantic_score', 0):.4f} lexical={result.get('lexical_score', 0):.4f}")
        return results
    def print_results(self, question, results):
        print("\n")
        print("=" * 70)
        print("TAI KHAMTI RETRIEVER RESULTS")
        print("=" * 70)
        print(f"Question: {question}")
        print(f"Results: {len(results)}")
        if not results:
            print("No relevant results found.")
            print("=" * 70)
            return
        for rank, result in enumerate(results, start=1):
            print("\n" + "-" * 70)
            print(f"RESULT {rank}")
            print("-" * 70)
            print("ID:", result.get("id", "N/A"))
            print("Source:", result.get("source", "N/A"))
            print("Matched field:", result.get("matched_field", "N/A"))
            print("Combined Score:", f"{result.get('score', 0.0):.4f}")
            print("Semantic Score:", f"{result.get('semantic_score', result.get('score', 0.0)):.4f}")
            print("Lexical Score:", f"{result.get('lexical_score', 0.0):.4f}")
            print("Category:", result.get("category", "Unknown"))
            print("Instruction:", result.get("instruction", ""))
            print("English:", result.get("english", ""))
            print("Tai Khamti:", result.get("tai_khamti", ""))
            print("Transliteration:", result.get("transliteration", ""))
        print("=" * 70)
def main():
    print("\n")
    print("=" * 70)
    print("TAI KHAMTI RETRIEVER TEST")
    print("=" * 70)
    retriever = TaiKhamtiRetriever(top_k=5, similarity_threshold=0.50)
    test_questions = [
        "What is good to eat here?",
        ". What is good to eat here?",
        "What are the daily activities of Tai Khamti people?",
        "Tell me about Tai Khamti culture.",
        "Where do Tai Khamti people live?",
        "What language do Tai Khamti people speak?",
        "What do Tai Khamti people do for work?"
    ]
    for question in test_questions:
        results = retriever.search(question=question, top_k=5)
        retriever.print_results(question, results)
    print("\n")
    print("=" * 70)
    print("RETRIEVER TEST COMPLETED")
    print("=" * 70)
if __name__ == "__main__":
    main()