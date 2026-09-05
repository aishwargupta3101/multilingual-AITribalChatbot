import json
from pathlib import Path
import faiss
import numpy as np

class TaiKhamtiRetriever:

    def __init__(
        self,
        top_k=4,
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

        self.model = None
        if not self.index_file.exists():
            raise FileNotFoundError(
                f"FAISS index not found:\n"
                f"{self.index_file}"
            )

        print("Loading FAISS index...")

        self.index = faiss.read_index(
            str(self.index_file)
        )
        print("FAISS index loaded.")

        if not self.documents_file.exists():
            raise FileNotFoundError(
                f"Documents file not found:\n"
                f"{self.documents_file}"
            )
        with open(
            self.documents_file,
            "r",
            encoding="utf-8"
        ) as file:
            self.documents = json.load(file)
        print(
            f"Loaded {len(self.documents)} documents."
        )

        if self.index.ntotal != len(self.documents):
            raise ValueError(
                "FAISS index and document count "
                "do not match.\n"
                f"FAISS: {self.index.ntotal}\n"
                f"Documents: {len(self.documents)}"
            )
        print(
            f"FAISS documents: {self.index.ntotal}"
        )
        print("Tai Khamti Retriever ready.")
        print("=" * 70)

    def load_model(self):
        """
        Load the embedding model only when it is needed.
        This prevents the model from consuming RAM during
        FastAPI startup.
        """

        if self.model is None:
            print("Loading Tai Khamti embedding model...")
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
            print("Embeddings model loaded.")

    def search(
        self,
        question: str,
        top_k=None
    ):
        if not question or not question.strip():
            return []
        question = question.strip()
        if top_k is None:
            top_k = self.top_k

        top_k = min(
            top_k,
            len(self.documents)
        )
        self.load_model()
        query_embedding = self.model.encode(
            [question],
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )
        scores, indices = self.index.search(
            query_embedding,
            top_k
        )
        results = []

        for rank, (score, index_id) in enumerate(
            zip(scores[0], indices[0]),
            start=1
        ):
            if index_id == -1:
                continue

            score = float(score)
            document = self.documents[
                int(index_id)
            ]
            print("\n" + "=" * 70)
            print(
                f"RETRIEVED DOCUMENT #{rank}"
            )
            print("=" * 70)
            print(
                "FAISS Index:",
                int(index_id)
            )
            print(
                "ID:",
                document.get(
                    "id",
                    "N/A"
                )
            )

            print(
                "Similarity:",
                f"{score:.4f}"
            )
            print(
                "Category:",
                document.get(
                    "category",
                    "Unknown"
                )
            )
            print(
                "English:",
                document.get(
                    "english",
                    ""
                )
            )
            print(
                "Tai Khamti:",
                document.get(
                    "tai_khamti",
                    ""
                )
            )
            print(
                "Transliteration:",
                document.get(
                    "transliteration",
                    ""
                )
            )
            print("=" * 70)

            if score < self.similarity_threshold:
                print(
                    f"Rejected: score {score:.4f} "
                    f"< threshold "
                    f"{self.similarity_threshold:.4f}"
                )
                continue

            results.append(
                {
                    "score": score,
                    "id": document.get(
                        "id",
                        "Unknown"
                    ),
                    "category": document.get(
                        "category",
                        "Unknown"
                    ),
                    "english": document.get(
                        "english",
                        ""
                    ),

                    "tai_khamti": document.get(
                        "tai_khamti",
                        ""
                    ),
                    "transliteration": document.get(
                        "transliteration",
                        ""
                    ),
                    "source": "TAI_KHAMTI"
                }
            )
        print("\n" + "=" * 70)
        print(
            "FINAL RETRIEVAL RESULTS:",
            len(results)
        )
        print("=" * 70)
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
            "Question:",
            question
        )
        print(
            "Results:",
            len(results)
        )

        if not results:
            print(
                "No relevant results found."
            )
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
                "Similarity:",
                f"{result.get('score', 0.0):.4f}"
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
tai_khamti_retriever = TaiKhamtiRetriever(
    top_k=4,
    similarity_threshold=0.50
)
def main():
    print("\n")
    print("=" * 70)
    print("TAI KHAMTI RETRIEVER TEST")
    print("=" * 70)
    retriever = TaiKhamtiRetriever(
        top_k=4,
        similarity_threshold=0.50
    )
    test_questions = [
        "What is Tai Khamti?",
        "Where do Tai Khamti people live?",
        "What language do Tai Khamti people speak?",
        "What are the daily activities of Tai Khamti people?",
        "Tell me about Tai Khamti culture."
    ]

    for question in test_questions:
        results = retriever.search(
            question=question,
            top_k=4
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