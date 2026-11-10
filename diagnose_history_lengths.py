"""
Read-only chat-history length diagnostic.
Uses the project's MongoDB connection object (mongodb.connect()).
Reads message lengths only; does not print message text or modify records.
Run from the project root with the virtual environment activated:
    python diagnose_history_lengths.py
"""
import asyncio
from datetime import datetime
from backend.database.connection import mongodb
from backend.database.collections import collections


async def main():
    print("=" * 72)
    print("CHAT HISTORY LENGTH DIAGNOSTIC — READ ONLY")
    print("=" * 72)
    print("Reads metadata and message lengths only. No message text is displayed.")
    try:
        await mongodb.connect()
        collection = collections.chat_history
        cursor = collection.find(
            {},
            {
                "_id": 0,
                "session_id": 1,
                "role": 1,
                "language": 1,
                "created_at": 1,
                "message": 1,
            },
        ).sort("created_at", -1).limit(20)
        docs = await cursor.to_list(length=20)
    except Exception as exc:
        print(f"Diagnostic could not read MongoDB: {type(exc).__name__}: {exc}")
        print("No records were changed. Check that MongoDB is available and the backend connection module exports 'mongodb'.")
        return

    if not docs:
        print("No chat history records were found.")
        return

    print("\nLatest messages (text is not displayed):")
    print("Date/time                 Role       Language       Chars   Approx words")
    print("-" * 72)
    session_counts = {}
    for doc in reversed(docs):
        message_text = doc.get("message", "")
        if not isinstance(message_text, str):
            message_text = str(message_text)
        role = str(doc.get("role", "unknown"))
        language = str(doc.get("language", "unknown"))
        created = doc.get("created_at")
        created_text = created.strftime("%Y-%m-%d %H:%M:%S") if isinstance(created, datetime) else str(created or "unknown")[:19]
        session_id = str(doc.get("session_id", "unknown"))
        session_counts[session_id] = session_counts.get(session_id, 0) + 1
        print(f"{created_text:25} {role[:10]:10} {language[:14]:14} {len(message_text):7d} {len(message_text.split()):14d}")

    assistant_docs = [doc for doc in docs if doc.get("role") == "assistant"]
    user_docs = [doc for doc in docs if doc.get("role") == "user"]
    print("\nSummary:")
    print(f"- Records inspected: {len(docs)}")
    print(f"- Distinct sessions in sample: {len(session_counts)}")
    if assistant_docs:
        lengths = [len(doc.get("message", "")) if isinstance(doc.get("message", ""), str) else len(str(doc.get("message", ""))) for doc in assistant_docs]
        print(f"- Assistant messages: {len(assistant_docs)}")
        print(f"- Longest assistant answer: {max(lengths)} characters")
        print(f"- Average assistant answer: {sum(lengths) / len(lengths):.0f} characters")
    if user_docs:
        lengths = [len(doc.get("message", "")) if isinstance(doc.get("message", ""), str) else len(str(doc.get("message", ""))) for doc in user_docs]
        print(f"- User messages: {len(user_docs)}")
        print(f"- Longest user message: {max(lengths)} characters")
    print("\nThis samples the 20 most recent records across all sessions.")
    print("It cannot identify the exact history used for a specific slow request.")
    print("No database records were changed.")


if __name__ == "__main__":
    asyncio.run(main())
