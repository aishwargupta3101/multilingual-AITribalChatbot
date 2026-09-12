"""
Image Search Service
Uses Wikimedia Commons to find relevant images.
"""
import logging
import re
import requests
logger = logging.getLogger(__name__)

class ImageService:
    API_URL = "https://commons.wikimedia.org/w/api.php"
    HEADERS = {
        "User-Agent": (
            "TribalAIChatbot/1.0 "
            "(educational multilingual tribal AI project)"
        )
    }
    def should_show_images(self, question: str) -> bool:

        if not question:
            return False
        question = question.lower()
        visual_keywords = [
            "house",
            "home",
            "housing",
            "building",
            "architecture",
            "dress",
            "clothes",
            "costume",
            "wear",
            "attire",
            "food",
            "dish",
            "cuisine",
            "meal",
            "festival",
            "celebration",
            "dance",
            "culture",
            "traditional",
            "tradition",
            "village",
            "temple",
            "monastery",
            "craft",
            "handicraft",
            "art",
            "weaving",
            "textile",
            "people",
            "community",
            "tribe",
            "look like",
            "what does",
            "show me",
            "photo",
            "picture",
            "image",
            "images"
        ]
        return any(
            keyword in question
            for keyword in visual_keywords
        )

    def _get_visual_category(
        self,
        question: str
    ) -> str:
        question = question.lower()

        categories = {
            "house": [
                "house",
                "home",
                "housing",
                "architecture",
                "building"
            ],
            "dress": [
                "dress",
                "clothes",
                "costume",
                "wear",
                "attire"
            ],
            "food": [
                "food",
                "dish",
                "cuisine",
                "meal"
            ],
            "festival": [
                "festival",
                "celebration"
            ],
            "dance": [
                "dance"
            ],
            "handicraft": [
                "craft",
                "handicraft",
                "art",
                "weaving",
                "textile"
            ],
            "people": [
                "people",
                "community",
                "tribe"
            ],
            "temple": [
                "temple",
                "monastery"
            ]
        }
        for category, keywords in categories.items():

            if any(
                keyword in question
                for keyword in keywords
            ):
                return category

        return ""
    def build_image_query(
        self,
        question: str,
        selected_language: str = "english"
    ) -> str:
        if not question:
            return ""
        question_lower = question.lower()
        category = self._get_visual_category(
            question
        )
        tai_khamti = any(
            keyword in question_lower
            for keyword in [
                "tai khamti",
                "khamti people",
                "khamti tribe",
                "khamti community",
                "khamti"
            ]
        )
        if tai_khamti:
            if category == "house":
                return "Tai Khamti traditional house"
            if category == "dress":
                return "Tai Khamti traditional dress"

            if category == "food":
                return "Tai Khamti traditional food"

            if category == "festival":
                return "Tai Khamti traditional festival"
            if category == "dance":
                return "Tai Khamti traditional dance"
            if category == "handicraft":
                return "Tai Khamti traditional handicraft"

            if category == "temple":
                return "Tai Khamti temple monastery"
            if category == "people":
                return "Tai Khamti people"
            return "Tai Khamti"
        if category == "house":
            return "traditional house architecture"
        if category == "dress":
            return "traditional dress costume"
        if category == "food":
            return "traditional food cuisine"
        if category == "festival":
            return "traditional festival celebration"
        if category == "dance":
            return "traditional dance"
        if category == "handicraft":
            return "traditional handicraft"
        if category == "temple":
            return "traditional temple monastery"
        if category == "people":
            return "traditional community people"

        return question.strip()

    def _tokenize(self, text: str) -> set:
        if not text:
            return set()
        words = re.findall(
            r"[a-zA-Z]{3,}",
            text.lower()
        )
        stopwords = {
            "the",
            "and",
            "are",
            "what",
            "which",
            "where",
            "when",
            "how",
            "does",
            "about",
            "this",
            "that",
            "with",
            "from",
            "their",
            "they",
            "them",
            "show",
            "tell",
            "give",
            "please",
            "image",
            "images",
            "photo",
            "picture",
            "traditional"
        }
        return {
            word
            for word in words
            if word not in stopwords
        }
    def _calculate_relevance(
        self,
        title: str,
        description: str,
        query: str
    ) -> float:

        title_tokens = self._tokenize(
            title
        )
        description_tokens = self._tokenize(
            description
        )
        query_tokens = self._tokenize(
            query
        )
        if not query_tokens:
            return 0.0
        title_matches = (
            query_tokens
            & title_tokens
        )
        description_matches = (
            query_tokens
            & description_tokens
        )

        title_score = (
            len(title_matches)
            / len(query_tokens)
        )
        description_score = (
            len(description_matches)
            / len(query_tokens)
        )
        score = (
            title_score * 0.75
            + description_score * 0.25
        )

        return score
    def _search_wikimedia(
        self,
        query: str,
        limit: int
    ) -> list:

        logger.info(
            f"Wikimedia search query: {query}"
        )
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srnamespace": 6,
            "srlimit": 10,
            "srprop": "title|snippet"
        }
        response = requests.get(
            self.API_URL,
            params=search_params,
            headers=self.HEADERS,
            timeout=15
        )

        response.raise_for_status()
        search_data = response.json()
        search_results = (
            search_data
            .get("query", {})
            .get("search", [])
        )
        if not search_results:
            return []
        titles = []

        for result in search_results:
            title = result.get("title")
            if title:
                titles.append(title)

        if not titles:
            return []
        image_params = {
            "action": "query",
            "format": "json",
            "prop": "imageinfo",
            "titles": "|".join(titles),
            "iiprop": "url|extmetadata",
            "iiurlwidth": 800
        }
        image_response = requests.get(
            self.API_URL,
            params=image_params,
            headers=self.HEADERS,
            timeout=15
        )
        image_response.raise_for_status()
        image_data = image_response.json()
        pages = (
            image_data
            .get("query", {})
            .get("pages", {})
        )
        images = []
        for page in pages.values():
            image_info = page.get(
                "imageinfo",
                []
            )
            if not image_info:
                continue
            info = image_info[0]

            image_url = (
                info.get("thumburl")
                or info.get("url")
            )
            if not image_url:
                continue
            metadata = info.get(
                "extmetadata",
                {}
            )
            description = (
                metadata
                .get(
                    "ImageDescription",
                    {}
                )
                .get(
                    "value",
                    ""
                )
            )
            title = (
                page.get(
                    "title",
                    ""
                )
                .replace(
                    "File:",
                    ""
                )
            )
            relevance = self._calculate_relevance(
                title=title,
                description=description,
                query=query
            )
            images.append(
                {
                    "title": title,
                    "url": image_url,
                    "description": description,
                    "relevance": relevance
                }
            )
        images.sort(
            key=lambda item: item.get(
                "relevance",
                0
            ),
            reverse=True
        )
        relevant_images = [
            image
            for image in images
            if image.get(
                "relevance",
                0
            ) >= 0.15
        ]
        logger.info(
            f"Wikimedia relevant images: "
            f"{len(relevant_images)}"
        )
        return relevant_images[:limit]
    def search_images(
        self,
        query: str,
        limit: int = 3
    ) -> list:
        if not query or not query.strip():
            return []
        query = query.strip()
        try:
            images = self._search_wikimedia(
                query=query,
                limit=limit
            )
            if images:
                logger.info(
                    f"Images found for query: {query}"
                )
                return images

        except Exception:
            logger.exception(
                f"Wikimedia search failed for: {query}"
            )
        logger.warning(
            f"No relevant Wikimedia images found "
            f"for query: {query}"
        )
        return []
image_service = ImageService()