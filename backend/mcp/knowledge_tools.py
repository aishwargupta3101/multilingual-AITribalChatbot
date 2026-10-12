
import json
import re
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "knowledge.json"
SUPPORTED_LANGUAGES = {"english", "hindi", "manipuri_meitei_mayek", "manipuri_bengali"}
SUPPORTED_CATEGORIES = {"education", "government", "daily_life", "employment"}

def load_knowledge():
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data.get("records", [])
    except (json.JSONDecodeError, OSError):
        return []

def normalize_text(text):
    return re.sub(r"\s+", " ", str(text).lower()).strip()

def search_knowledge(query, language="english", category="all", limit=5):
    query = normalize_text(query)
    if not query:
        return {"success": False, "message": "Query cannot be empty.", "results": []}
    if language not in SUPPORTED_LANGUAGES:
        return {"success": False, "message": "Unsupported language.", "results": []}
    if category != "all" and category not in SUPPORTED_CATEGORIES:
        return {"success": False, "message": "Unsupported category.", "results": []}
    keywords = set(query.split())
    results = []
    for record in load_knowledge():
        if category != "all" and record.get("category") != category:
            continue
        content = record.get("content", {})
        text = normalize_text(content.get(language, ""))
        title = normalize_text(record.get("title", ""))
        searchable = f"{title} {text}"
        score = sum(1 for word in keywords if word in searchable)
        if score:
            results.append({
                "id": record.get("id"),
                "title": record.get("title"),
                "category": record.get("category"),
                "language": language,
                "content": content.get(language, ""),
                "source_name": record.get("source_name", ""),
                "source_url": record.get("source_url", ""),
                "verified_on": record.get("verified_on", ""),
                "relevance_score": score
            })
    results.sort(key=lambda item: item["relevance_score"], reverse=True)
    return {
        "success": True,
        "query": query,
        "language": language,
        "total_results": len(results),
        "results": results[:max(1, min(limit, 10))]
    }

def get_knowledge_categories():
    return sorted(SUPPORTED_CATEGORIES)

def get_official_links(query, limit=10):
    query = normalize_text(query)
    links = []
    for record in load_knowledge():
        url = record.get("source_url", "")
        title = normalize_text(record.get("title", ""))
        if url and query in title:
            links.append({
                "title": record.get("title", ""),
                "source_name": record.get("source_name", ""),
                "url": url,
                "verified_on": record.get("verified_on", "")
            })
    return links[:max(1, min(limit, 20))]