import html
import streamlit as st

from api.client import APIClient
from api.endpoints import UPLOAD_ENDPOINT


def html_block(content):
    """
    Render custom HTML correctly in Streamlit.
    """
    content = " ".join(
        line.strip()
        for line in content.splitlines()
        if line.strip()
    )
    st.markdown(
        content,
        unsafe_allow_html=True
    )

def show_upload():
    language = st.session_state.get(
        "language",
        "english"
    )
    language_name = language.replace(
        "_",
        " "
    ).title()
    html_block(
        f"""
        <div class="documents-page-header">

            <div class="documents-header-content">

                <div class="documents-header-icon">
                    📄
                </div>

                <div>

                    <div class="documents-header-title">
                        Knowledge Documents
                    </div>

                    <div class="documents-header-subtitle">
                        Add documents to expand Tribal AI's knowledge.
                    </div>

                </div>

            </div>

            <div class="documents-header-language">
                🌐 {language_name}
            </div>

        </div>
        """
    )
    html_block(
        f"""
        <div class="documents-intro">

            <div class="documents-intro-title">
                Knowledge Base
            </div>

            <div class="documents-intro-text">
                Documents uploaded here will be stored and searched
                only within the <b>{language_name}</b> knowledge base.
            </div>

        </div>
        """
    )
    html_block(
        """
        <div class="upload-card">

            <div class="upload-card-header">

                <div class="upload-card-icon">
                    ⬆️
                </div>

                <div>

                    <div class="upload-card-title">
                        Upload a Knowledge Document
                    </div>

                    <div class="upload-card-subtitle">
                        Add PDFs, DOCX files, or text documents
                        containing information you want Tribal AI
                        to learn from.
                    </div>

                </div>

            </div>

        </div>
        """
    )
    uploaded_file = st.file_uploader(
        "Choose a document",
        type=["pdf", "docx", "txt"],
        key="knowledge_document_uploader"
    )
    if uploaded_file:
        file_name = html.escape(
            uploaded_file.name
        )
        file_size_kb = uploaded_file.size / 1024
        html_block(
            f"""
            <div class="document-selected-file">

                <div class="document-file-icon">
                    📄
                </div>

                <div class="document-file-info">

                    <div class="document-file-name">
                        {file_name}
                    </div>

                    <div class="document-file-size">
                        {file_size_kb:.2f} KB
                    </div>

                </div>

            </div>
            """
        )
        if st.button(
            "⬆ Upload to Knowledge Base",
            type="primary",
            use_container_width=True,
            key="upload_knowledge_document"
        ):
            with st.spinner(
                f"Adding document to {language_name} knowledge base..."
            ):
                try:
                    response = APIClient.upload(
                        UPLOAD_ENDPOINT,
                        uploaded_file,
                        st.session_state.session_id,
                        language
                    )
                    html_block(
                        """
                        <div class="document-success-card">

                            <div class="document-success-icon">
                                ✓
                            </div>

                            <div>

                                <div class="document-success-title">
                                    Document uploaded successfully
                                </div>

                                <div class="document-success-text">
                                    The document has been added to
                                    the selected language knowledge base.
                                </div>

                            </div>

                        </div>
                        """
                    )

                    if isinstance(response, dict):

                        with st.expander(
                            "View Upload Details"
                        ):
                            st.json(response)

                except Exception as error:
                    error_message = html.escape(
                        str(error)
                    )
                    html_block(
                        f"""
                        <div class="document-error-card">

                            <div class="document-error-title">
                                Upload failed
                            </div>

                            <div class="document-error-text">
                                {error_message}
                            </div>

                        </div>
                        """
                    )
    st.markdown(
        "<div style='height:18px'></div>",
        unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns(
        3,
        gap="medium"
    )
    with col1:
        html_block(
            """
            <div class="document-info-card">

                <div class="document-info-icon">
                    📄
                </div>

                <div class="document-info-title">
                    Supported Files
                </div>

                <div class="document-info-text">
                    PDF, DOCX and TXT documents are supported.
                </div>

            </div>
            """
        )
    with col2:
        html_block(
            """
            <div class="document-info-card">

                <div class="document-info-icon">
                    ⬆️
                </div>

                <div class="document-info-title">
                    File Upload
                </div>

                <div class="document-info-text">
                    Upload documents to expand the AI knowledge base.
                </div>

            </div>
            """
        )
    with col3:
        html_block(
            """
            <div class="document-info-card">

                <div class="document-info-icon">
                    🌐
                </div>

                <div class="document-info-title">
                    Language Specific
                </div>

                <div class="document-info-text">
                    Documents stay within the selected language
                    knowledge base.
                </div>

            </div>
            """
        )
    html_block(
        """
        <div class="documents-footer">
            Tribal AI • Knowledge preservation through multilingual AI
        </div>
        """
    )