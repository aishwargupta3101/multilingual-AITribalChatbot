from backend.rag.hybrid_retriever import hybrid_retriever
from data.tai_khamti.tai_khamti_retriever import TaiKhamtiRetriever
from backend.llm.llama_service import llama_service


class RAGService:
    def __init__(self):
        print("=" * 70)
        print("INITIALIZING RAG SERVICE")
        print("=" * 70)
        self.tai_khamti_retriever = TaiKhamtiRetriever(
            top_k=4
        )
        print("Tai Khamti RAG initialized successfully.")
    def build_context(
        self,
        question: str,
        vector_db_path: str = None
    ):
        if vector_db_path:
            print("=" * 70)
            print("USING UPLOADED DOCUMENT RAG")
            print("Vector DB:", vector_db_path)
            print("=" * 70)

            documents = hybrid_retriever.retrieve(
                question=question,
                vector_db_path=vector_db_path,
                k=4
            )
            if not documents:
                return {
                    "context": "",
                    "sources": []
                }

            context = "\n\n".join(
                document.page_content
                for document in documents
            )
            sources = []
            for document in documents:
                sources.append(
                    {
                        "source": document.metadata.get(
                            "source",
                            "UPLOADED_DOCUMENT"
                        ),
                        "chunk": document.metadata.get(
                            "chunk",
                            "Unknown"
                        ),
                        "category": document.metadata.get(
                            "category",
                            "Unknown"
                        )
                    }
                )
            return {
                "context": context,
                "sources": sources
            }
        print("=" * 70)
        print("USING TAI KHAMTI KNOWLEDGE BASE")
        print("Question:", question)
        print("=" * 70)

        results = self.tai_khamti_retriever.search(
            question,
            top_k=4
        )

        print(
            "Tai Khamti results:",
            len(results)
        )
        MIN_SIMILARITY = 0.55
        results = [
            result
            for result in results
            if result.get("score", 0.0) >= MIN_SIMILARITY
        ]

        print(
            "Results after similarity filtering:",
            len(results)
        )

        if not results:

            print(
                "No relevant Tai Khamti results found."
            )

            return {
                "context": "",
                "sources": []
            }

        context_parts = []
        sources = []

        for index, result in enumerate(results):

            print("-" * 70)
            print("Result:", index + 1)
            print("ID:", result.get("id"))
            print("Score:", result.get("score"))
            print("Category:", result.get("category"))

            context_parts.append(
                f"Category: {result.get('category', 'Unknown')}\n"
                f"English: {result.get('english', '')}"
            )
            sources.append(
                {
                    "id": result.get(
                        "id",
                        "Unknown"
                    ),
                    "category": result.get(
                        "category",
                        "Unknown"
                    ),
                    "score": "Tai Khamti Knowledge Base",
                    "similarity": result.get(
                        "score",
                        0.0
                    )
                }
            )

        context = "\n\n".join(
            context_parts
        )
        print("=" * 70)
        print("TAI KHAMTI CONTEXT CREATED")
        print("Context length:", len(context))
        print("Sources:", sources)
        print("=" * 70)

        return {
            "context": context,
            "sources": sources
        }

    async def generate_answer(
        self,
        question: str,
        vector_db_path: str = None,
        context: str = "",
        sources: list = None
    ):
        """
        Generate an answer using RAG context and Llama.
        """
        print("=" * 70)
        print("RAG GENERATE ANSWER")
        print("Question:", question)
        print("=" * 70)
        if sources is None:
            sources = []
        if not context.strip():
            rag_result = self.build_context(
                question=question,
                vector_db_path=vector_db_path
            )
            context = rag_result.get(
                "context",
                ""
            )
            sources = rag_result.get(
                "sources",
                []
            )
        if not context.strip():
            answer = (
                "I couldn't find that information "
                "in the Tai Khamti knowledge base."
            )
            return {
                "answer": answer,
                "sources": []
            }
        prompt = f"""
You are a helpful AI assistant for the Tai Khamti community.

Answer the user's question using ONLY the information
explicitly present in the provided knowledge.

STRICT RULES:

1. Do NOT use your own general knowledge.
2. Do NOT invent facts.
3. Do NOT make assumptions.
4. Do NOT use information that is not present in the context.
5. Do NOT combine unrelated entries to create an answer.
6. If the answer cannot be directly found in the knowledge,
   reply exactly:

I couldn't find that information in the Tai Khamti knowledge base.

Always answer in English.

TAI KHAMTI KNOWLEDGE:
{context}

QUESTION:
{question}

ANSWER:
"""
        conversation = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        answer = await llama_service.generate_response(
            conversation
        )

        if not answer:

            answer = (
                "I couldn't generate an answer."
            )

        print("=" * 70)
        print("RAG ANSWER GENERATED")
        print("Answer:", answer)
        print("=" * 70)
        return {
            "answer": answer,
            "sources": sources
        }
rag_service = RAGService()