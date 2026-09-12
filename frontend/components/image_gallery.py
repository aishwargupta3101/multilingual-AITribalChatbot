import streamlit as st
import requests
from PIL import Image
from io import BytesIO

WIKIMEDIA_HEADERS = {
    "User-Agent": (
        "TribalAI/1.0 "
        "(multilingual tribal knowledge assistant)"
    )
}
@st.cache_data(
    ttl=3600,
    show_spinner=False
)
def download_image(image_url):
    try:
        response = requests.get(
            image_url,
            headers=WIKIMEDIA_HEADERS,
            timeout=15
        )
        response.raise_for_status()
        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()
        if not content_type.startswith("image/"):
            return None
        return response.content
    except Exception:
        return None
def render_images(images):

    if not images:
        return
    st.markdown(
        """
        <div class="image-gallery-header">
            <div class="image-gallery-icon">📷</div>
            <div>
                <div class="image-gallery-title">
                    Related Images
                </div>
                <div class="image-gallery-subtitle">
                    Visual references related to your question
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    valid_images = []
    for image in images:
        if not isinstance(image, dict):
            continue
        image_url = image.get("url")

        if not image_url:
            continue

        image_bytes = download_image(
            image_url
        )
        if not image_bytes:
            continue

        try:
            image_object = Image.open(
                BytesIO(image_bytes)
            )
            image_object.load()
            valid_images.append(
                {
                    "image": image_object.copy(),
                    "title": image.get(
                        "title",
                        "Related image"
                    )
                }
            )
        except Exception:
            continue

    if not valid_images:
        return
    columns = st.columns(
        min(3, len(valid_images)),
        gap="medium"
    )
    for index, item in enumerate(valid_images):
        with columns[
            index % len(columns)
        ]:
            st.image(
                item["image"],
                width="stretch"
            )
            title = item["title"]

            if title:
                st.caption(
                    title
                )