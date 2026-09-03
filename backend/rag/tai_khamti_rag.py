from data.tai_khamti.tai_khamti_retriever import TaiKhamtiRetriever
class TaiKhamtiRAG:

    def __init__(self, top_k=4):
        print("=" * 70)
        print("TAI KHAMTI RAG SYSTEM")
        print("=" * 70)
        print("\nInitializing Tai Khamti Retriever...")
        self.retriever = TaiKhamtiRetriever(
            top_k=top_k
        )
        self.top_k = top_k
        print("Tai Khamti RAG initialized successfully.")

    def retrieve(self, question, top_k=None):
        if top_k is None:
            top_k = self.top_k

        results = self.retriever.search(
            question=question,
            top_k=top_k
        )
        return results
    def build_context(
        self,
        question,
        vector_db_path=None,
        language="english",
        top_k=None
    ):
        results = self.retrieve(
            question,
            top_k=top_k
        )
        if not results:
            return {
                "context": "",
                "sources": []
            }
        context_parts = []
        sources = []
        for result in results:
            if language.lower() in [
                "tai_khamti",
                "tai khamti"
            ]:
                context_parts.append(
                    f"Category: {result.get('category', 'Unknown')}\n"
                    f"English: {result.get('english', '')}\n"
                    f"Tai Khamti: {result.get('tai_khamti', '')}"
                )
            else:
                context_parts.append(
                    f"Category: {result.get('category', 'Unknown')}\n"
                    f"English: {result.get('english', '')}"
                )
            sources.append(
                {
                    "source": "Language knowledge Base",
                    "chunk": result.get(
                        "id",
                        "Unknown"
                    ),
                    "id": result.get(
                        "id",
                        "Unknown"
                    ),
                    "category": result.get(
                        "category",
                        "Unknown"
                    ),
                    "score": result.get(
                        "score",
                        0.0
                    ),
                    "similarity": result.get(
                        "score",
                        0.0
                    )
                }
            )
        context = "\n\n".join(
            context_parts
        )
        return {
            "context": context,
            "sources": sources
        }
tai_khamti_rag = TaiKhamtiRAG(
    top_k=4
)