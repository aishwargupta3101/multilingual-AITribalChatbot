import asyncio

from backend.database.connection import mongodb


async def main():
    await mongodb.connect()

    docs = await mongodb.database.documents.find(
        {},
        {
            "filename": 1,
            "language": 1,
            "vector_db_path": 1
        }
    ).to_list(None)

    for doc in docs:
        print(
            doc.get("language"),
            "|",
            doc.get("filename"),
            "|",
            doc.get("vector_db_path")
        )

    await mongodb.disconnect()


asyncio.run(main())