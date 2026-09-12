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
    def __init__(
        self,
        top_k=5,
        similarity_threshold=0.50
    ):
        print("=" * 70)
        print("INITIALIZING TAI KHAMTI RETRIEVER")
        print("=" * 70)
        base_dir = Path(__file__).parent
        self.index_file = (
            base_dir
            / "faiss_index"
            / "tai_khamti_combined.index"
        )
        self.documents_file = (
            base_dir
            / "faiss_index"
            / "tai_khamti_combined_documents.json"
        )
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
        """
        Normalize text for exact matching.

        Example:

            ". What is good to eat here?"
            "What is good to eat here?"

        become the same normalized string.
        """
        if not text:
            return ""
        text = str(text).lower().strip()
        text = re.sub(
            r"[^\w\s]",
            " ",
            text,
            flags=re.UNICODE
        )
        text = re.sub(
            r"\s+",
            " ",
            text
        )
        return text.strip()

    @staticmethod
    def tokenize(text):
        """
        Convert text into lowercase word tokens.
        """
        normalized = TaiKhamtiRetriever.normalize_text(text)
        if not normalized:
            return set()
        return set(normalized.split())

    def load_database(self):
        if (
            self.index is not None
            and self.documents is not None
        ):
            return
        print("=" * 70)
        print("LOADING TAI KHAMTI DATABASE")
        print("=" * 70)

        import faiss
        if not self.index_file.exists():
            raise FileNotFoundError(
                f"Tai Khamti FAISS index not found: "
                f"{self.index_file}"
            )
        if not self.documents_file.exists():
            raise FileNotFoundError(
                f"Tai Khamti documents not found: "
                f"{self.documents_file}"
            )

        print("Loading FAISS index...")
        self.index = faiss.read_index(
            str(self.index_file)
        )
        print("FAISS index loaded.")
        print("Loading Tai Khamti documents...")

        with open(
            self.documents_file,
            "r",
            encoding="utf-8"
        ) as file:
            self.documents = json.load(file)

        if not isinstance(self.documents, list):
            raise ValueError(
                "Tai Khamti documents JSON must contain a list."
            )
        print(
            f"Loaded {len(self.documents)} documents."
        )
        print(
            f"FAISS documents: "
            f"{self.index.ntotal}"
        )

        if self.index.ntotal != len(self.documents):
            print(
                "WARNING: FAISS index size and "
                "document count are different."
            )
        print("Tai Khamti database loaded successfully.")

    def load_model(self):

        if self.model is not None:
            return
        print("=" * 70)
        print("LOADING TAI KHAMTI EMBEDDING MODEL")
        print("=" * 70)
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )
        print("Tai Khamti embedding model loaded.")

    def exact_match_search(
        self,
        question
    ):
        """
        Search exact English or Tai Khamti text.

        Returns:
            dict or None
        """
        self.load_database()
        normalized_question = (
            self.normalize_text(question)
        )
        if not normalized_question:
            return None

        for document in self.documents:
            english = self.normalize_text(
                document.get("english", "")
            )
            if (
                english
                and english == normalized_question
            ):
                result = dict(document)
                result["score"] = 1.0
                result["source"] = "TAI_KHAMTI_EXACT"
                print(
                    "EXACT TAI KHAMTI ENGLISH MATCH FOUND"
                )
                print(
                    f"ID: {document.get('id', 'N/A')}"
                )
                return result

        for document in self.documents:
            tai_khamti = self.normalize_text(
                document.get("tai_khamti", "")
            )
            if (
                tai_khamti
                and tai_khamti == normalized_question
            ):
                result = dict(document)
                result["score"] = 1.0
                result["source"] = "TAI_KHAMTI_EXACT"
                print(
                    "EXACT TAI KHAMTI TEXT MATCH FOUND"
                )
                print(
                    f"ID: {document.get('id', 'N/A')}"
                )
                return result
        return None
    def lexical_score(
        self,
        question,
        document
    ):
        """
        Lightweight word-overlap score.

        This helps prevent FAISS from selecting completely
        unrelated sentences when the semantic similarity
        is weak.
        """
        query_tokens = self.tokenize(question)
        if not query_tokens:
            return 0.0
        english = document.get(
            "english",
            ""
        )
        category = document.get(
            "category",
            ""
        )
        document_text = (
            f"{english} {category}"
        )
        document_tokens = self.tokenize(
            document_text
        )
        if not document_tokens:
            return 0.0
        overlap = (
            query_tokens.intersection(
                document_tokens
            )
        )
        return (
            len(overlap)
            / max(len(query_tokens), 1)
        )
    def semantic_search(
        self,
        question,
        top_k=None
    ):
        self.load_database()
        self.load_model()

        import numpy as np
        if top_k is None:
            top_k = self.top_k
        candidate_k = min(
            max(top_k * 3, 10),
            self.index.ntotal
        )
        embedding = self.model.encode(
            [question],
            normalize_embeddings=True
        )
        embedding = np.asarray(
            embedding,
            dtype="float32"
        )

        scores, indices = self.index.search(
            embedding,
            candidate_k
        )
        candidates = []

        for score, index_position in zip(
            scores[0],
            indices[0]
        ):
            if index_position < 0:
                continue
            if index_position >= len(
                self.documents
            ):
                continue
            document = self.documents[
                index_position
            ]
            semantic_score = float(score)
            lexical_score = self.lexical_score(
                question,
                document
            )

            combined_score = (
                semantic_score * 0.80
                +
                lexical_score * 0.20
            )
            result = dict(document)
            result["semantic_score"] = (
                semantic_score
            )
            result["lexical_score"] = (
                lexical_score
            )
            result["score"] = (
                combined_score
            )
            result["source"] = (
                "TAI_KHAMTI_SEMANTIC"
            )
            candidates.append(result)

        candidates.sort(
            key=lambda item: item.get(
                "score",
                0.0
            ),
            reverse=True
        )
        final_results = []
        seen_ids = set()
        for result in candidates:
            result_id = result.get(
                "id"
            )
            if result_id in seen_ids:
                continue
            seen_ids.add(
                result_id
            )
            if (
                result["semantic_score"]
                < self.similarity_threshold
            ):
                continue
            final_results.append(
                result
            )
            if len(final_results) >= top_k:
                break
        return final_results

    def search(
        self,
        question,
        top_k=None
    ):
        """
        Main Tai Khamti search.

        Priority:

        1. Exact match
        2. Multi-document semantic retrieval
        3. Return several documents for RAG
        """
        if not question:
            return []
        if top_k is None:
            top_k = self.top_k
        print("\n" + "=" * 70)
        print("TAI KHAMTI SEARCH")
        print("=" * 70)
        print(
            f"Question: {question}"
        )
        exact_result = (
            self.exact_match_search(
                question
            )
        )
        if exact_result:
            print(
                "Returning exact verified match."
            )
            return [
                exact_result
            ]
        print(
            "No exact match."
        )
        print(
            "Performing multi-document semantic search..."
        )
        results = self.semantic_search(
            question=question,
            top_k=top_k
        )
        print(
            f"Retrieved {len(results)} "
            f"Tai Khamti documents."
        )
        for rank, result in enumerate(
            results,
            start=1
        ):
            print(
                f"{rank}. "
                f"ID={result.get('id', 'N/A')} "
                f"score={result.get('score', 0):.4f} "
                f"semantic={result.get('semantic_score', 0):.4f} "
                f"lexical={result.get('lexical_score', 0):.4f}"
            )
        return results
    def print_results(
        self,
        question,
        results
    ):
        print("\n")
        print("=" * 70)
        print("TAI KHAMTI RETRIEVER RESULTS")
        print("=" * 70)
        print(
            f"Question: {question}"
        )
        print(
            f"Results: {len(results)}"
        )
        if not results:
            print(
                "No relevant results found."
            )
            print("=" * 70)
            return

        for rank, result in enumerate(
            results,
            start=1
        ):
            print("\n" + "-" * 70)
            print(
                f"RESULT {rank}"
            )
            print("-" * 70)
            print(
                "ID:",
                result.get(
                    "id",
                    "N/A"
                )
            )
            print(
                "Combined Score:",
                f"{result.get('score', 0.0):.4f}"
            )
            print(
                "Semantic Score:",
                f"{result.get('semantic_score', result.get('score', 0.0)):.4f}"
            )
            print(
                "Lexical Score:",
                f"{result.get('lexical_score', 0.0):.4f}"
            )
            print(
                "Category:",
                result.get(
                    "category",
                    "Unknown"
                )
            )
            print(
                "English:",
                result.get(
                    "english",
                    ""
                )
            )
            print(
                "Tai Khamti:",
                result.get(
                    "tai_khamti",
                    ""
                )
            )
            print(
                "Transliteration:",
                result.get(
                    "transliteration",
                    ""
                )
            )
        print("=" * 70)

def main():
    print("\n")
    print("=" * 70)
    print("TAI KHAMTI RETRIEVER TEST")
    print("=" * 70)
    retriever = TaiKhamtiRetriever(
        top_k=5,
        similarity_threshold=0.50
    )
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
        results = retriever.search(
            question=question,
            top_k=5
        )
        retriever.print_results(
            question,
            results
        )
    print("\n")
    print("=" * 70)
    print("RETRIEVER TEST COMPLETED")
    print("=" * 70)

if __name__ == "__main__":
    main()