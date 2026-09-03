from pathlib import Path
import sys

BASE_DIR = Path(__file__).parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))
from tai_khamti_retriever import TaiKhamtiRetriever

class TaiKhamtiRAG:
    def __init__(self, top_k=3):
        print("\n" + "=" * 70)
        print("TAI KHAMTI RAG SYSTEM")
        print("=" * 70)
        print("\nInitializing Tai Khamti Retriever...")
        self.retriever = TaiKhamtiRetriever(
            top_k=top_k
        )
        self.top_k = top_k

        print("\nTai Khamti RAG initialized successfully.")
    def retrieve(self, question, top_k=None):
        if not question or not question.strip():
            return []
        results = self.retriever.search(
            question,
            top_k=top_k
        )

        return results
    def build_context(self, results):
        if not results:
            return ""
        context_parts = []

        for rank, result in enumerate(
            results,
            start=1
        ):
            context = (
                f"Document {rank}\n"
                f"ID: {result.get('id', 'N/A')}\n"
                f"Source: {result.get('source', 'N/A')}\n"
                f"Category: {result.get('category', 'N/A')}\n"
                f"English: {result.get('english', 'N/A')}\n"
                f"Tai Khamti: {result.get('tai_khamti', 'N/A')}\n"
                f"Transliteration: "
                f"{result.get('transliteration', 'N/A')}\n"
            )
            context_parts.append(context)

        return "\n" + "\n".join(context_parts)
    def create_prompt(
        self,
        question,
        results
    ):
        context = self.build_context(
            results
        )
        prompt = f"""
You are a multilingual AI assistant for the Tai Khamti community.

Use the retrieved knowledge below to answer the user's question.

IMPORTANT RULES:

1. Use the retrieved information when it is relevant.
2. Do not invent facts that are not supported by the retrieved information.
3. Give a simple and clear answer.
4. If the user asks in English, answer in English.
5. If the user asks for Tai Khamti, provide the Tai Khamti answer from the knowledge base when available.
6. If the retrieved information does not contain the answer, clearly say that the information is not available in the current knowledge base.
7. Do not mention FAISS, embeddings, retrieval, or internal system details to the user.
RETRIEVED KNOWLEDGE:
{context}
USER QUESTION:
{question}

ANSWER:
"""

        return prompt
    def query(
        self,
        question,
        top_k=None
    ):
        if not question or not question.strip():
            return {
                "question": question,
                "results": [],
                "context": "",
                "prompt": ""
            }
        results = self.retrieve(
            question,
            top_k=top_k
        )
        context = self.build_context(
            results
        )
        prompt = self.create_prompt(
            question,
            results
        )
        return {
            "question": question,
            "results": results,
            "context": context,
            "prompt": prompt
        }
    def print_results(
        self,
        question,
        rag_result
    ):
        print("\n" + "=" * 70)
        print("RAG QUERY")
        print("=" * 70)
        print(
            "\nQuestion:",
            question
        )
        results = rag_result.get(
            "results",
            []
        )

        if not results:
            print(
                "\nNo relevant knowledge found."
            )
            return

        print(
            f"\nRetrieved {len(results)} documents:"
        )
        for rank, result in enumerate(
            results,
            start=1
        ):
            print(
                "\n" + "-" * 70
            )
            print(
                f"Result {rank}"
            )
            print(
                "Similarity:",
                f"{result.get('score', 0.0):.4f}"
            )
            print(
                "ID:",
                result.get(
                    "id",
                    "N/A"
                )
            )
            print(
                "Source:",
                result.get(
                    "source",
                    "N/A"
                )
            )
            print(
                "Category:",
                result.get(
                    "category",
                    "N/A"
                )
            )
            print(
                "English:",
                result.get(
                    "english",
                    "N/A"
                )
            )
            print(
                "Tai Khamti:",
                result.get(
                    "tai_khamti",
                    "N/A"
                )
            )
            transliteration = result.get(
                "transliteration",
                ""
            )
            if transliteration:
                print(
                    "Transliteration:",
                    transliteration
                )
        print(
            "\n" + "=" * 70
        )
        print(
            "GENERATED RAG PROMPT"
        )
        print(
            "=" * 70
        )
        print(
            rag_result.get(
                "prompt",
                ""
            )
        )
def main():
    print("\n")
    print("=" * 70)
    print("TAI KHAMTI RAG TEST")
    print("=" * 70)
    rag = TaiKhamtiRAG(
        top_k=3
    )
    test_questions = [
        "What is artificial intelligence?",
        "What is machine learning?",
        "What is clean energy transition?",
        "What is the immune system?",
        "How can I protect my online privacy?",
        "Why is sleep important for health?"
    ]
    for question in test_questions:
        rag_result = rag.query(
            question
        )
        rag.print_results(
            question,
            rag_result
        )
    print("\n")
    print("=" * 70)
    print("TAI KHAMTI RAG TEST COMPLETED")
    print("=" * 70)
if __name__ == "__main__":
    main()